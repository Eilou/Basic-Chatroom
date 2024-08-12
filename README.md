# Basic Chatroom
*By Louie Brooks*

This was written as a little project to learn how to use websockets in Python. The end goal with it 
being so I could write myself a basic websocket server to host API projects on.

It was developed over July/August of 2024 using Python version 3.11.1

## Deployment

**Server Side**
```bash
python Server.py
```

**Client Side**
```bash
python Client.py
```

## Commands
Run the following when the server is connected to at least one client

### Server Side

`/reset`
- Resets the server's rooms and closes all connections

`/broadcast/<message>`
- Sends a message to all connected clients

`/rbroadcast/<room>/<message>`
- Sends a message to all connected clients within a specified room

`/individual/<room>/<message>`
- Sends a message to a specific client

`/rooms`
- Outputs a list of rooms and the clients connected in each

`/dcUser/<user>`
- Disconnects a specific user/client from the server

`/dcRoom/<room>`
- Disconnects all users within a room from the server

### Client Side

`/changeRoom/<room>`
- Moves the user from one room to another