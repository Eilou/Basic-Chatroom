import websockets
import asyncio
import sys

from CustomExitException import *

CLIENTS = set()
 
# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)
 
async def receive(websocket):
    while True:
        received = await websocket.recv()
        received = "\t\t\t" + received
        print(received)

async def send(websocket):
    while True:
        toSend = await ainput("")
        if toSend.strip() == "exit":
            raise CustomExitException("Connection closing")
        
        await websocket.send(toSend)

# Creating WebSocket server
async def ws_server(websocket):
    print("WebSocket: Server started and Client connected.")
    CLIENTS.add(websocket)
    await websocket.send("Client connected")
    try:
        await asyncio.gather(
            receive(websocket),
            send(websocket)
            )
    except CustomExitException as e:
        print("Connection closed")
    finally:
        CLIENTS.remove(websocket)
    
    
 
async def main():
    async with websockets.serve(ws_server, "0.0.0.0", 7890):
        await asyncio.Future()  # run forever
 
# basically __name__ is a special method which changes relative to how the module is run, if directly then it is __main__, else it is set to be the name of the file
if __name__ == "__main__":
    asyncio.run(main())