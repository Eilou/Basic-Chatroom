import websockets
import asyncio
import sys
import json


from CustomExitException import *

# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' ')) # might explain the space at the start  of each line
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

async def receive(ws):
    while True:
        received_str = await ws.recv()
        received_dict = json.loads(received_str)
        received = f'\t\t\t{received_dict["user_id"]}: {received_dict["message"].strip()}'
        print(received)

async def send(ws, user_id, room_id):
    while True:
        toSend = await ainput("")

        if toSend.strip() == "/exit":
            raise CustomExitException()

        send_dict = {
            "message": toSend,
            "user_id": str(user_id), # may be best to have this in an object but hey ho
            "room_id": room_id
        }
        await ws.send(json.dumps(send_dict))            

 
# The main function that will handle connection and communication
# with the server
async def ws_client():

    try:
        
        # url = "ws://192.168.40.164:8765" # using my private ip as a temporary gig
        url = "ws://localhost:8765"

        # Connect to the server
        async with websockets.connect(url) as ws:
            
            receieved = await ws.recv()
            user_id = await ws.recv()
            room_request_message = await ws.recv()

            print(f'{receieved} with id: {user_id}')
            print("------------------------------------")

            room_id = input(room_request_message)
            await ws.send(room_id) # may not need this id, as it is stored on the server but it is good to have access to regardless 
            
            await asyncio.gather(
                receive(ws),
                send(ws, user_id, room_id)
            )
            
    except CustomExitException:
        print("--------------------------------------------")
        print("You have closed your connection to the server")
    except websockets.exceptions.ConnectionClosedOK:
        print("Cannot connect to server")
 
# Start the connection
asyncio.run(ws_client())