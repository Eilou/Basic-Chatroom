# Basic Chatroom
*By Louie Brooks*

This was written as a little project to learn how to use websockets in Python. The end goal with it 
being so I could write myself a basic websocket server to host API projects on.

It was developed over July/August of 2024 using Python version 3.11.1

## Deployment

### Setting up based on your network
This system can be ran on either your device (easiest but least useful), local network (easy enough) or over the Internet (bit of a faff).

In the file `Client.py` within the first few lines of the `ws_client()` function, there is defined the IP address/URL of the server. In the `Server.py` in the `main()` function there is defined the IP address/URL to host to the server on.

For both of these match the port number. I have set it as default to `8765`, but you can change it if you want. Just be warned that some port numbers are already used by default by some applications on computers.

*On your Device*
1. Set the `Server.py` URL to be either `0.0.0.0` (broadcast address) or `127.0.0.1` (loopback address). You could even just write `localhost` here if you were feeling adventurous.
2. Set the `Client.py` URL to be that same IP address or instead set it to `localhost`. Ensure the client side URL is formatted as `ws://<IP ADDRESS HERE>:8765`.

*Local Network Hosting*
1. Set the `Server.py` URL to be either `0.0.0.0` (broadcast address).
2. On the device you are hosting the server, open up `cmd` or some form of bash terminal like `git bash` and type `ipconfig`. Read your IPv4 address (should be a private address typically beginning with `192.168.x.y`).
3. Set the `Client.py` URL to be that IPv4 address. Ensure the client side is formatted as `ws://<IP ADDRESS HERE>:8765`.

*Over the Internet*
1. On the device you want to host the server on (run the `Server.py` file on), open up a web browser, go to Google and type "What is my IP Address?"
2. Google should give you an answer which will be your public IP address. This is how the rest of the world sees your local network. It is the IP address of your router.
3. Then on this same device open up `cmd` or some form of bash terminal like `git bash` and type `ipconfig`. Read your default gateway (should be a private address typically beginning with `192.168.x.y`).
4. Take this and put it into a web browser's URL bar and it should redirect you to your router's settings (as your router is your default gateway). Sometimes for this step, you can't be connected through Wifi so should connect through an Ethernet cable, however in doing so you should redo step `1` and `2` as connecting through hardware rather than wireless sometimes changes your IP address (it shouldn't but it may if your network is set up as weirdly as mine is). Another thing to mention is that sometimes routers don't let you connect through `http` so make sure to add `https` when accessing the settings.
5. Type in your login details.
6. Go through some sort of advanced settings to find a setting about **Port Forwarding**. They like to hide this setting, not sure why though.
7. Add a new port forwarding configuration (may also require you to add you server hosting devices private IP address for this - *see Local Network Hosting: step 2*) specific to port `8765`, or whatever you have changed it to in the code, set this same port for both the internal and external port numbers, select TCP and UDP connections. BAM! Port forwarding set up, now any frame which comes through with the port number 8765 will be directed to your computer.
8. Go to your `Server.py` file and set the url to be `0.0.0.0` (broadcast address) so you listen for any frames coming into the network.
9. On the other device, go to the `Client.py` file and set the URL to be the public IP address of the computer acting like a server. Ensure the client side is formatted as `ws://<IP ADDRESS HERE>:8765`.

Okay so hopefully those guides are comprehensive enough to show you how to prepare the system, now its time to run it!

### Starting the system from the terminal

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

`/changeName/<name>`
- Changes or sets a users name