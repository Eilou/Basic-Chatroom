import websockets
import asyncio
import sys

# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

async def receive(ws):
    while True:
        received = await ws.recv()
        received = "\t\t\t" + received
        print(received)

async def send(ws):
    while True:
        toSend = await ainput("")
        if toSend == "exit":
            raise websockets.AbortHandshake()
        
        await ws.send(toSend)

 
# The main function that will handle connection and communication
# with the server
async def ws_client():

    try:
        
        url = "ws://127.0.0.1:7890"
        # Connect to the server
        async with websockets.connect(url) as ws:
            
            receieved = await ws.recv()
            print(f'WebSocket: Client connection status: {receieved}')
            
            
            await asyncio.gather(
                receive(ws),
                send(ws)
            )
            
    except websockets.AbortHandshake:
        print("--------------------------------------------")
        print("You have closed your connection to the server")
    except websockets.ConnectionClosedOK:
        print("Cannot connect to server")
 
# Start the connection
asyncio.run(ws_client())