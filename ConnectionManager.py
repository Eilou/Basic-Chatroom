# this will hold all the different connections and rooms to enable data transfer

class ConnectionManager:

    def __init__(self, room_count : int) -> None:
        self.connections = {} # {"user_id" : websocket_object}
        self.rooms = {} # {"room_id" : {"user_id_1", "user_id_2"}}
        self.names = {} # {"user_id" : "name"}
        
        self.rooms = {}
        for i in range (room_count):
            self.rooms[str(i+1)] = set()

    def resetRooms(self) -> None:
        self.rooms = {}
    
    def resetConnections(self, room_count=10) -> None:
        for i in range (room_count):
            self.rooms[str(i+1)] = set()
    
    def resetServer(self) -> None:
        self.resetRooms()
        self.resetConnections()

    def getRoomMembers(self, room_id) -> set:
        return self.rooms[room_id]
    
    def addToRoom(self, room_id, user_id) -> None:
        self.rooms[room_id].add(user_id)

    # disconnect a particular user
    async def disconnect(self, user_id) -> None:
        await self.connections[user_id].close()

    async def disconnectAll(self) -> None:
        for user_id in self.connections:
            await self.connections[user_id].close()

    async def disconnectRoom(self, room_id) -> None:
        for user_id in self.rooms[room_id]:
            await self.connections[user_id].close()

    def setName(self, user_id, name) -> None:
        self.names[user_id] = name
    