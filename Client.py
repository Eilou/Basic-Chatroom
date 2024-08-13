import websockets
import asyncio
import sys
import json

from Exceptions.CustomExitException import CustomExitException
from Exceptions.MalformedCommandException import MalformedCommandException

# this file should not contain any connection manager (as it would need to be updated constantly and this would be lame, plus security)

client_details = {
    "user_id" : "-1",
    "room_id" : "-1"
}

# https://stackoverflow.com/questions/58454190/python-async-waiting-for-stdin-input-while-doing-other-stuff by user: user4815162342
async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+'')) # might explain the space at the start  of each line
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

async def receive(ws):
    while True:
        received_str = await ws.recv()
        received_dict : dict = json.loads(received_str)
        
        name_prequel = ""
        if "name" in received_dict:
            name_prequel = f'{received_dict["name"]} '
            
        received = f'\t\t\t{name_prequel}({received_dict["user_id"]}) : {received_dict["message"].strip()}'
        print(received)

async def send(ws, user_id):
    while True:
        message = await ainput("")
        command_status = False

        if message[0] == "/":
            command_status = True
            
        # even if it is a command we still want to let the server know what was said
        send_dict = {
            "message": message,
            "user_id": str(user_id), # may be best to have this in an object but hey ho
            "command_status": command_status
            }
        await ws.send(json.dumps(send_dict)) 
 
# The main function that will handle connection and communication
# with the server
async def ws_client():

    try:
        
        url = "ws://localhost:8765"

        # Connect to the server
        async with websockets.connect(url) as ws:
            
            receieved = await ws.recv()
            user_id = await ws.recv()
            room_request_message = await ws.recv()
            room_count = int(await ws.recv())

            print(f'{receieved} with id: {user_id}')
            print("------------------------------------")

            
            room_id = input(room_request_message)

            while (int(room_id) < 1 or int(room_id) > room_count):
                print("Please enter a valid room number")
                room_id = input(room_request_message)

            await ws.send(room_id) # may not need this id, as it is stored on the server but it is good to have access to regardless 
            
            await asyncio.gather(
                receive(ws),
                send(ws, user_id)
            )
            
    except CustomExitException:
        print("--------------------------------------------")
        print("You have closed your connection to the server")
    except websockets.exceptions.ConnectionClosedOK:
        print("Cannot connect to server")
 
# Start the connection
asyncio.run(ws_client())