import websockets
import asyncio
import sys
import json 

from CustomExitException import *
from MalformedCommandException import *
 

from ConnectionManager import *

connectionManager = ConnectionManager(10) 
# connections = {} # id: websocket object

# rooms = {} # room id : set of websocket ids
# for i in range (10):
#     rooms[str(i+1)] = set()


# think this works but not 100% sure if this is how global stuff works
# def resetConnections():
#     global connections
#     connections = {}


# def resetRooms():
#     global rooms

#     rooms = {}
#     for i in range (10):
#         rooms[str(i+1)] = set()

# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)
 
# receive and forward the message on
async def receive(websocket : websockets.WebSocketServerProtocol, connectionManager : ConnectionManager):
    while True:
        received_str = await websocket.recv()
        received_dict = json.loads(received_str)
        
        received = f'\t\t\t{received_dict["user_id"]}: {received_dict["message"].strip()}' # format the message 
        print(received)

        # find out which room the user who send the message was in and then room broadcast it there
        room_to_send = received_dict["room_id"]

        await room_broadcast(connectionManager, received_str, room_to_send, received_dict["user_id"])
        
# send a message to all in every room
async def broadcast(connectionManager : ConnectionManager, message : dict, sender_id : str):
    for user_id in connectionManager.getConnections():
        if user_id != sender_id:
            await connectionManager.getUserConnection(user_id).send(message)

# send a message to all in a specific room
async def room_broadcast(connectionManager : ConnectionManager, message : dict, room_id : str, sender_id : str):
    users_in_room = connectionManager.getRoomMembers(room_id)
    for user_id in users_in_room:
        if user_id != sender_id:
            await connectionManager.getUserConnection(user_id).send(message)
    
    
# holds the commands possible to be ran by the server
async def commands(connectionManager : ConnectionManager, message: str):
    message = message[1:].strip()
    command = message
    if message.find("/") != -1: 
        message = message.split("/") # example command format: /command/arg1/arg2
        command = message[0]

    match command:

        case "reset": #/reset
            await connectionManager.resetServer()
            raise CustomExitException()

        case "broadcast": #/broadcast/message Inserted
        
            if len(message) != 2: # number of arguments
                raise MalformedCommandException("/broadcast requires 2 arguments")
            
            toSend_dict = {
                "message" : message[1],
                "user_id": "Server"
            }
            await broadcast(connectionManager ,json.dumps(toSend_dict), -1) # -1 to indicate server broadcast to all

        case "rbroadcast": #/rbroadcast/target_room/message Inserted
        
            if len(message) != 3: # number of arguments
                raise MalformedCommandException("/rbroadcast requires 3 arguments")
            
            target_room_id = message[1].strip()
            connectionManager.checkRoomExists(target_room_id)

            toSend_dict = {
                "message" : message[2],
                "user_id": "Server"
            }
            await room_broadcast(connectionManager, json.dumps(toSend_dict), target_room_id, -1) 

            
    
        case "individual": # /individual/2/message Inserted
            if len(message) != 3: 
                raise MalformedCommandException("/individual requires 3 arguments")
            
            target_user_id = message[1].strip()
            connectionManager.checkUserExists(target_user_id)

            toSend_dict = {
                "message" : message[2],
                "user_id": "Server"
            }
            await connectionManager.getUserConnection(target_user_id).send(json.dumps(toSend_dict))


        case _:
            raise MalformedCommandException("Unknown command")

# server send means broadcast to all
async def send(connectionManager : ConnectionManager):
    while True:
        message = await ainput("")
        
        # the below section should probably be reworked
        try:
            if message[0] == "/":
                await commands(connectionManager, message)

        except MalformedCommandException as e:
            print(f"{e.message}")
                    

# Creating WebSocket server
async def ws_server(websocket):

    global connectionManager

    user_id = connectionManager.getNextUserID()
    connectionManager.connections[user_id] = websocket
    
    print(f"Conncection to client {user_id} established")
    print("------------------------------------")
    
    await websocket.send("Connected to server") # let client know its in
    await websocket.send(str(user_id)) # let the client know which id to transmit messages as    

    await websocket.send(f'Which room do you want to be placed in (1 - {len(connectionManager.getRooms())}): ')
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
    except websockets.exceptions.ConnectionClosedOK:
        print("------------------------------------")
        print(f'Client {user_id} disconnected')
    
 
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
# 4. oh my god i need to refactor some of these functions into a different file
# 1. close a specific connection
# 2. allow clients to change rooms
# 5. allow users to set a name which is the bit visible to others, not their id
# 3. clean up outputs (say which message is from where on the server side)
