# this will hold all the different connections and rooms to enable data transfer
import websockets

from Exceptions.MalformedCommandException import MalformedCommandException

class ConnectionManager:

    def __init__(self, room_count : int) -> None:
        self.connections = {} # {"user_id" : websocket_object}
        self.rooms = {} # {"room_id" : {"user_id_1", "user_id_2"}}

        self.users = {} # {"user_id" : {"connection" : websocket_object, "room_id" : "1", "name" : "jimmy"}}
        
        self.resetRooms() # default is 10
    
    def addToRoom(self, room_id, user_id) -> None:
        self.rooms[room_id].add(user_id)

    # disconnect a particular user
    async def disconnectUser(self, user_id) -> None:
        await self.connections[user_id].close()

    async def disconnectAll(self) -> None:
        for user_id in self.connections:
            await self.connections[user_id].close()

    async def disconnectRoom(self, room_id) -> None:
        for user_id in self.rooms[room_id]:
            await self.connections[user_id].close()

    def removeFromRoom(self, room_id, user_id) -> None:
        print("room id " + room_id)
        print("room contents " + str(self.rooms[room_id]))
        print(user_id)
        self.rooms[room_id].remove(user_id)

    # the below 2 could maybe be refactored into other functions
    def checkRoomExists(self, room_id):
        try:
            targetRoom = self.rooms[room_id] # this will raise a key error if doesn't exist
        except KeyError:
            raise MalformedCommandException(f'Room {room_id} does not exist')

    def checkUserExists(self, user_id):
        try:
            target_connection = self.connections[user_id]
        except KeyError:
            raise MalformedCommandException(f'User {user_id} does not exist')

    def changeUserRoom(self, room_id_initial, room_id_final, user_id):
        self.removeFromRoom(room_id_initial, user_id)
        self.addToRoom(room_id_final, user_id)

    ######################################
    ## getters and setters (and resets) ## 
    ######################################

    def getConnections(self) -> dict:
        return self.connections
    
    def getUserConnection(self, user_id) -> websockets.WebSocketServerProtocol:
        return self.connections[user_id]

    def getRooms(self) -> dict:
        return self.rooms

    def resetRooms(self, room_count=10) -> None:
        for i in range (room_count):
            self.rooms[str(i+1)] = set()

    async def resetConnections(self) -> None:
        for user_id in self.connections:
            await self.getUserConnection(user_id).close()
        self.connections = {}
    
    async def resetServer(self) -> None:
        self.resetRooms()
        self.resetConnections()

    def getRoomMembers(self, room_id) -> set:
        return self.rooms[room_id]
    
    def getNextUserID(self) -> str:
        return str(len(self.connections)+1)
    