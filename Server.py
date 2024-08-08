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



    

# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)
 
async def receive(websocket):
    while True:
        received_str = await websocket.recv()
        received_dict = json.loads(received_str)
        
        received = f'\t\t\t{received_dict["id"]}: {received_dict["message"].strip()}'
        print(received)
        
        await broadcast(received_str, received_dict["id"])
        
# send a message to all in every room
async def broadcast(message, senderid):
    for connection_id in connections:
        if connection_id != senderid:
            await connections[connection_id].send(message)

# send a message to all in a specific room
async def room_broadcast(message, senderid, room_id):
    users_in_room = rooms[room_id]
    for user_id in users_in_room:
        await connections[user_id].send(message)
    
    
# holds the commands possible to be ran by the server
async def commands(connections, rooms: set, message: str):
    message = message[1:]
    
    message = message.split("/") # example command format: /command/arg1/arg2
    
    command = message[0]

    match command:
        case "broadcast": #/broadcast/message Inserted
        
            if len(message) != 2: # number of arguments
                raise MalformedCommandException()
            
            toSend_dict = {
                "message" : message[1],
                "id": "Server"
            }
            await broadcast(json.dumps(toSend_dict), -1) # -1 to indicate server broadcast to all
    
        case "individual": # /individual/2/message Inserted
            if len(message) != 3: 
                raise MalformedCommandException()
            
            target = message[1].strip()
            try:
                target_exception = connections[target]
            except KeyError:
                raise MalformedCommandException("Target User ID is not connected")
            
            toSend_dict = {
                    "message" : message[2],
                    "id": "Server"
                }
            
            await connections[target].send(json.dumps(toSend_dict))
        
        case _:
            raise MalformedCommandException()
        
        
    

# server send means broadcast to all
async def send():
    while True:
        message = await ainput("")
        if message.strip() == "exit": # this doesn't really work
            raise CustomExitException()
        
        # the below section should probably be reworked
        try:
            if message[0] == "/":
                await commands(connections, rooms, message)
        except MalformedCommandException as e:
            print(f"{e.message}")
                    

# Creating WebSocket server
async def ws_server(websocket):
    id = str(len(connections)+1)
    connections[id] = websocket
    
    print(f"Conncection to client {id} established")
    print("------------------------------------")
    
    await websocket.send("Connected to server") # let client know its in
    await websocket.send(str(id)) # let the client know which id to transmit messages as    
    
    await websocket.send(f'Which room do you want to be placed in (1 - {len(rooms)}): ')
    room_id = await websocket.recv()
    rooms[room_id].add(id)
    # for room in rooms:
    #     print(rooms[room])
    
    # if a message has to be sent to a specific client put it in the above block before the await
    
    try:
        await asyncio.gather(
            receive(websocket),
            send()
            )
    
    except CustomExitException:
        print("------------------------------------")
        print("Connection closed as per request")
    except websockets.exceptions.ConnectionClosedOK:
        print("------------------------------------")
        print(f'Client {id} disconnected')
    
 
async def main():
    print("Server starting")
    # host_ip = "0.0.0.0"
    host_ip = "localhost"
    async with websockets.serve(ws_server, host_ip, 8765):
        await asyncio.Future()  # run forever
 
# basically __name__ is a special method which changes relative to how the module is run, if directly then it is __main__, else it is set to be the name of the file
if __name__ == "__main__":
    asyncio.run(main())