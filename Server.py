import websockets
import asyncio
import sys
import json 

from CustomExitException import *
from MalformedCommandException import *
 
connections = {} # id: websocket object

rooms = {} # room id : set of websocket ids
for i in range (10):
    rooms[str(i+1)] = set()


# think this works but not 100% sure if this is how global stuff works
def resetConnections():
    global connections
    connections = {}


def resetRooms():
    global rooms

    rooms = {}
    for i in range (10):
        rooms[str(i+1)] = set()

# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)
 
# receive and forward the message on
async def receive(websocket):
    while True:
        received_str = await websocket.recv()
        received_dict = json.loads(received_str)
        
        received = f'\t\t\t{received_dict["user_id"]}: {received_dict["message"].strip()}' # format the message 
        print(received)

        # find out which room the user who send the message was in and then room broadcast it there
        room_to_send = received_dict["room_id"]

        await room_broadcast(received_str, room_to_send, received_dict["user_id"])
        
# send a message to all in every room
async def broadcast(message, senderid):
    for connection_id in connections:
        if connection_id != senderid:
            await connections[connection_id].send(message)

# send a message to all in a specific room
async def room_broadcast(message, room_id, senderid):
    users_in_room = rooms[room_id]
    for user_id in users_in_room:
        if user_id != senderid:
            await connections[user_id].send(message)
    
    
# holds the commands possible to be ran by the server
async def commands(connections, rooms: set, message: str):
    message = message[1:].strip()
    command = message
    if message.find("/") != -1: 
        message = message.split("/") # example command format: /command/arg1/arg2
        command = message[0]

    match command:

        case "removeAll": #/removeAll
            for connection_id in connections:
                resetConnections()
                resetRooms()
                await connections[connection_id].close()
            raise CustomExitException()

        case "broadcast": #/broadcast/message Inserted
        
            if len(message) != 2: # number of arguments
                raise MalformedCommandException("/broadcast requires 2 arguments")
            
            toSend_dict = {
                "message" : message[1],
                "user_id": "Server"
            }
            await broadcast(json.dumps(toSend_dict), -1) # -1 to indicate server broadcast to all

        case "rbroadcast": #/rbroadcast/target_room/message Inserted
        
            if len(message) != 3: # number of arguments
                raise MalformedCommandException("/rbroadcast requires 3 arguments")
            
            target_room_id = message[1].strip()

            try:
                target_room = rooms[target_room_id] # exists to check that the room does actually exist and raise an error if not
                toSend_dict = {
                    "message" : message[2],
                    "user_id": "Server"
                }
                await room_broadcast(json.dumps(toSend_dict), target_room_id, -1) 

            except KeyError:
                raise MalformedCommandException("Target room does not exist")
    
        case "individual": # /individual/2/message Inserted
            if len(message) != 3: 
                raise MalformedCommandException("/individual requires 3 arguments")
            
            target_user_id = message[1].strip()

            try:
                target_connection = connections[target_user_id]
                toSend_dict = {
                    "message" : message[2],
                    "user_id": "Server"
                }
                await target_connection.send(json.dumps(toSend_dict))

            except KeyError:
                raise MalformedCommandException("Target user is not connected")

        case _:
            raise MalformedCommandException("Unknown command")

# server send means broadcast to all
async def send():
    while True:
        message = await ainput("")
        
        # the below section should probably be reworked
        try:
            if message[0] == "/":
                await commands(connections, rooms, message)
        except MalformedCommandException as e:
            print(f"{e.message}")
                    

# Creating WebSocket server
async def ws_server(websocket):
    user_id = str(len(connections)+1)
    connections[user_id] = websocket
    
    print(f"Conncection to client {user_id} established")
    print("------------------------------------")
    
    await websocket.send("Connected to server") # let client know its in
    await websocket.send(str(user_id)) # let the client know which id to transmit messages as    

    await websocket.send(f'Which room do you want to be placed in (1 - {len(rooms)}): ')
    room_id = await websocket.recv()
    rooms[room_id].add(user_id)
    
    # if a message has to be sent to a specific client put it in the above block before the await
    
    try:
        await asyncio.gather(
            receive(websocket),
            send()
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