import websockets
import asyncio
import sys
import json 

from Exceptions.CustomExitException import CustomExitException
from Exceptions.MalformedCommandException import MalformedCommandException
 
from ConnectionManager import *
from User import *


connectionManager = ConnectionManager(10) 

# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+''))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

# creates a formatted dictionary ready for sending
def createMessageDict(message : str, user_id : str) -> dict:
    return {
        "message" : message,
        "user_id": user_id
        }

async def clientCommands(websocket : websockets.WebSocketServerProtocol, connectionManager : ConnectionManager, received_dict : dict, received_user : User):
    message = received_dict["message"][1:].strip()
    command = message
    if message.find("/") != -1: 
        message = message.split("/") # example command format: /command/arg1/arg2
        command = message[0]

    match command:

        case "changeRoom": # /changeRoom/<room>
            
            if len(message) != 2: # number of arguments
                raise MalformedCommandException("/changeRoom requires 2 arguments")

            connectionManager.checkRoomExists(message[1])
            connectionManager.changeUserRoom(received_user.room_id, message[1], received_dict["user_id"])
            await websocket.send(json.dumps(createMessageDict(f'Changed from room {received_user.room_id} to room {message[1]}', "Server")))
        
        case _:
            raise MalformedCommandException("Unknown command")

# receive and forward the message on
async def receive(websocket : websockets.WebSocketServerProtocol, connectionManager : ConnectionManager):
    while True:
        received_str = await websocket.recv()
        received_dict = json.loads(received_str)
        
        # need to lookup user id to find which room they are in, then use this as the room to send to
        received_user : User = connectionManager.getUsers()[received_dict["user_id"]]


        received = f'\t\t\tUser {received_dict["user_id"]} (Room {received_user.room_id}): {received_dict["message"].strip()}' # format the message 
        print(received)

        # broadcast the message to the (user who sent it)'s room

        if received_dict["command_status"]:
            try:
                await clientCommands(websocket, connectionManager, received_dict, received_user)

            except MalformedCommandException as e:

                # await connectionManager.getUserConnection(target_user_id).send(json.dumps(toSend_dict))
                await websocket.send(json.dumps(createMessageDict(e.message, "Server")))
                # await individual(connectionManager, json.dumps(toSend_dict), rece, -1)
        else:
            await room_broadcast(connectionManager, received_str, received_user.room_id, received_dict["user_id"])
        
# send a message to all in every room
async def broadcast(connectionManager : ConnectionManager, message : dict, sender_id : str):
    for user_id in connectionManager.getUsers(): # returns the dict {"user_id" : {userobject}}
        if user_id != sender_id:
            await connectionManager.getUserConnection(user_id).send(message)

# send a message to all in a specific room
async def room_broadcast(connectionManager : ConnectionManager, message : dict, room_id : str, sender_id : str):
    users_in_room = connectionManager.getRoomMembers(room_id) # returns the user objects
    for user in users_in_room:
        if user.user_id != sender_id:
            await user.connection.send(message)
            # await connectionManager.getUserConnection(user_id).send(message)
    
    
# holds the commands possible to be ran by the server
async def serverCommands(connectionManager : ConnectionManager, message: str):
    message = message[1:].strip()
    command = message
    if message.find("/") != -1: 
        message = message.split("/") # example command format: /command/arg1/arg2
        command = message[0]

    match command:

        case "reset": # /reset

            if type(message) == list and len(message) != 1:
                raise MalformedCommandException("/reset requires no additional arguments") # apparently this line is unreachable according to pybalance, well buddy, I reached it. 

            await connectionManager.resetServer()
            raise CustomExitException()

        case "broadcast": # /broadcast/message Inserted
        
            if len(message) != 2: # number of arguments
                raise MalformedCommandException("/broadcast requires 2 arguments")
            
            await broadcast(connectionManager ,json.dumps(createMessageDict(message[1], "Server")), -1) # -1 to indicate server broadcast to all


        case "rbroadcast": # /rbroadcast/target_room/message Inserted
        
            if len(message) != 3: # number of arguments
                raise MalformedCommandException("/rbroadcast requires 3 arguments")
            
            target_room_id = message[1].strip()
            connectionManager.checkRoomExists(target_room_id)

            await room_broadcast(connectionManager, json.dumps(createMessageDict(message[2], "Server")), target_room_id, -1) 

    
        case "individual": # /individual/2/message Inserted
            if len(message) != 3: 
                raise MalformedCommandException("/individual requires 3 arguments")
            
            target_user_id = message[1].strip()
            connectionManager.checkUserExists(target_user_id)

            await connectionManager.getUserConnection(target_user_id).send(json.dumps(createMessageDict(message[2], "Server")))

        case "rooms": # /rooms
            if type(message) == list and len(message) != 1:
                raise MalformedCommandException("/rooms requires no additional arguments") # apparently this line is unraechable according to pybalance, well buddy, I reached it. 

            output = ""
            for room_id in connectionManager.getRooms():
                output += f'Room {room_id}:\n'
                for user in connectionManager.getRoomMembers(room_id):
                    output += str(user) + "\n"
            print(output)

        case "users": # /users
            if type(message) == list and len(message) != 1:
                raise MalformedCommandException("/users requires no additional arguments") # apparently this line is unraechable according to pybalance, well buddy, I reached it. 

            output = ""
            for user_id in connectionManager.getUsers():
                output += f'User {user_id}: {str(connectionManager.users[user_id])}'
                output += "\n"
            print(output)

        case "dcUser": # /dcUser/<user_id>
            if len(message) != 2:
                raise MalformedCommandException("/dcUser requires 2 arguments")
            
            target_user_id = message[1].strip()
            connectionManager.checkUserExists(target_user_id)
            await connectionManager.disconnectUser(target_user_id)

        case "dcRoom": # /dcRoom/<room_id>
            if len(message) != 2:
                raise MalformedCommandException("/dcUser requires 2 arguments")
            
            target_room_id = message[1].strip()
            connectionManager.checkRoomExists(target_room_id)
            await connectionManager.disconnectRoom(target_room_id)

        case _:
            raise MalformedCommandException("Unknown command")

# server send means broadcast to all
async def send(connectionManager : ConnectionManager):
    while True:
        message = await ainput("")
        
        # the below section should probably be reworked
        try:
            if message[0] == "/":
                await serverCommands(connectionManager, message)

        except MalformedCommandException as e:
            print(f"{e.message}")
                    

# Creating WebSocket server
async def ws_server(websocket):

    global connectionManager

    # specific to this instance of ws_sever
    # this value will be differnet for each client connected
    user_id = connectionManager.getNextUserID()

    user = User(user_id, websocket)
    connectionManager.users.update({user_id : user})

    print(f"Connection to client {user_id} established")
    print("------------------------------------")
    
    await websocket.send("Connected to server") # let client know its in
    await websocket.send(str(user_id)) # let the client know which id to transmit messages as    

    await websocket.send(f'Which room do you want to be placed in (1 - {len(connectionManager.getRooms())}): ')
    await websocket.send(str(len(connectionManager.getRooms())))

    room_id = await websocket.recv()
    connectionManager.addToRoom(room_id, user_id)
    
    # if a message has to be sent to a specific client put it in the above block before the await
    
    try:
        await asyncio.gather(
            receive(websocket, connectionManager),
            send(connectionManager)
            )
    
    except CustomExitException:
        print("------------------------------------")
        print("Connections closed as per request")
    except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError):
        print("------------------------------------")
        print(f'Client {user_id} disconnected')
        connectionManager.cleanUpUser(user_id)
    
 
async def main():
    print("Server starting")
    # host_ip = "0.0.0.0"
    host_ip = "localhost"
    async with websockets.serve(ws_server, host_ip, 8765):
        await asyncio.Future()  # run forever
 
# basically __name__ is a special method which changes relative to how the module is run, if directly then it is __main__, else it is set to be the name of the file
if __name__ == "__main__":
    asyncio.run(main())




#############
# TO DO
# 4. oh my god i need to refactor some of these functions into a different file /
# 1. close a specific connection 
# 2. allow clients to change rooms
# 5. allow users to set a name which is the bit visible to others, not their id
# 3. clean up outputs (say which message is from where on the server side)


# going to have to refactor how the connection manager holds user info