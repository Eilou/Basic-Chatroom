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

async def receive(ws):
    while True:
        received_str = await ws.recv()
        received_dict = json.loads(received_str)
        received = f"\t\t\t{received_dict["id"]}: {received_dict["message"].strip()}"
        print(received)

async def send(ws, id):
    while True:
        toSend = await ainput("")
        if toSend.strip() == "exit":
            raise CustomExitException()
        
        send_dict = {
            "message": toSend,
            "id": str(id) # may be best to have this in an object but hey ho
        }
        await ws.send(json.dumps(send_dict))

 
# The main function that will handle connection and communication
# with the server
async def ws_client():

    try:
        
        url = "ws://192.168.40.164:8765" # using my private ip as a temporary gig
        
        # Connect to the server
        async with websockets.connect(url) as ws:
            
            receieved = await ws.recv()
            id = await ws.recv()
            
            print(f'{receieved} with id: {id}')
            print("------------------------------------")
            
            await asyncio.gather(
                receive(ws),
                send(ws, id)
            )
            
    except CustomExitException:
        print("--------------------------------------------")
        print("You have closed your connection to the server")
    except websockets.ConnectionClosedOK:
        print("Cannot connect to server")
 
# Start the connection
asyncio.run(ws_client())