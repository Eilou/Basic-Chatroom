import websockets
import asyncio
import sys
import json 

from CustomExitException import *
 
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

# FOR THE CONNECTION MANAGER, ON FIRST CONNECTION THE SERVER ASSIGNS AN ID, THEN THE USER MUST COMMUNICATE THIS ID EVERY TIME THEY SEND A MESSAGEs

async def send(websocket):
    while True:
        messageToSend = await ainput("")
        if messageToSend.strip() == "exit":
            raise CustomExitException()
        
        toSend_dict = {
            "message" : messageToSend.strip(),
            "id": "Server"
        }
        await websocket.send(json.dumps(toSend_dict))

# Creating WebSocket server
async def ws_server(websocket):
    print("Conncection to client established")
    print("------------------------------------")
    await websocket.send("Connected to server") # let client know its in
    # await websocket.send({})
    try:
        await asyncio.gather(
            receive(websocket),
            send(websocket)
            )
    except CustomExitException:
        print("------------------------------------")
        print("Connection closed as per request")
    except websockets.exceptions.ConnectionClosedOK:
        print("------------------------------------")
        print("Socket closed as client disconnected")
    
 
async def main():
    async with websockets.serve(ws_server, "localhost", 8765):
        await asyncio.Future()  # run forever
 
# basically __name__ is a special method which changes relative to how the module is run, if directly then it is __main__, else it is set to be the name of the file
if __name__ == "__main__":
    asyncio.run(main())