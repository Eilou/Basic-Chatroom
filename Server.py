import websockets
import asyncio
import sys
import json 

from CustomExitException import *
 
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
    

# FOR THE CONNECTION MANAGER, ON FIRST CONNECTION THE SERVER ASSIGNS AN ID, THEN THE USER MUST COMMUNICATE THIS ID EVERY TIME THEY SEND A MESSAGEs

# async def send(websocket):
#     while True:
#         messageToSend = await ainput("")
#         if messageToSend.strip() == "exit":
#             raise CustomExitException()
        
#         toSend_dict = {
#             "message" : messageToSend.strip(),
#             "id": "Server"
#         }
#         await websocket.send(json.dumps(toSend_dict))


# server send means broadcast to all
async def send():
    while True:
        messageToSend = await ainput("")
        if messageToSend.strip() == "exit":
            raise CustomExitException()
        
        if messageToSend.find("/") == -1:
            toSend_dict = {
                "message" : messageToSend.strip(),
                "id": "Server"
            }
            await broadcast(json.dumps(toSend_dict), -1) # -1 to indicate server broadcast to all
        else:
            messageToSend = messageToSend.split("/")
            toSend_dict = {
                "message" : messageToSend[1].strip(),
                "id": "Server"
            }
            await connections[messageToSend[0].strip()].send(json.dumps(toSend_dict))
            # await broadcast(json.dumps(toSend_dict), messageToSend[0].strip()) # use a command in format "id/message" to decide who to send it to
            
            

# Creating WebSocket server
async def ws_server(websocket):
    id = str(len(connections)+1)
    connections[id] = websocket
    
    print(f"Conncection to client {id} established")
    print("------------------------------------")
    
    await websocket.send("Connected to server") # let client know its in
    await websocket.send(str(id)) # let the client know which id to transmit messages as
    
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