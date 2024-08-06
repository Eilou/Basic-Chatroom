import websockets
import asyncio
import sys
import json 

from CustomExitException import *
from MalformedCommandException import *
 
connections = {} # id: websocket object

rooms = {} # room id : set of websocket ids
for i in range (10):
    rooms[i] = set()
    

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
        
        
async def broadcast(message, senderid):
    for connection_id in connections:
        if connection_id != senderid:
            
            await connections[connection_id].send(message)
    
async def commands(connections, rooms: set, message: str):
    message = message[1:]
    
    message = message.split("/") # example command format: /command/arg1/arg2
    
    command = message[0]

    # if message.find(" ") != -1:
    #     command = message[0:message.find(" ")]
    
    if command == "broadcast": #/broadcast/message Inserted
        
        if len(message) != 2: # number of arguments
            raise MalformedCommandException()
        
        toSend_dict = {
            "message" : message[1],
            "id": "Server"
        }
        await broadcast(json.dumps(toSend_dict), -1) # -1 to indicate server broadcast to all
    
    elif command == "individual": # /individual/2/message Inserted
        if len(message) != 3: 
            raise MalformedCommandException()
        
        target = message[1]
        
        toSend_dict = {
                "message" : message[2],
                "id": "Server"
            }
        await connections[target.strip()].send(json.dumps(toSend_dict))
        
        
    

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
        
        # if message.find("/") == -1:
        #     toSend_dict = {
        #         "message" : message.strip(),
        #         "id": "Server"
        #     }
        #     await broadcast(json.dumps(toSend_dict), -1) # -1 to indicate server broadcast to all
        # else:
        #     message = message.split("/")
        #     toSend_dict = {
        #         "message" : message[1].strip(),
        #         "id": "Server"
        #     }
        #     await connections[message[0].strip()].send(json.dumps(toSend_dict))
        #     # await broadcast(json.dumps(toSend_dict), message[0].strip()) # use a command in format "id/message" to decide who to send it to
            
            

# Creating WebSocket server
async def ws_server(websocket):
    id = str(len(connections)+1)
    connections[id] = websocket
    
    print(f"Conncection to client {id} established")
    print("------------------------------------")
    
    await websocket.send("Connected to server") # let client know its in
    await websocket.send(str(id)) # let the client know which id to transmit messages as
    
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
        print("Socket closed as client disconnected")
    
 
async def main():
    print("Server starting")
    async with websockets.serve(ws_server, "localhost", 8765):
        await asyncio.Future()  # run forever
 
# basically __name__ is a special method which changes relative to how the module is run, if directly then it is __main__, else it is set to be the name of the file
if __name__ == "__main__":
    asyncio.run(main())