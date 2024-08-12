# this will hold all the different connections and rooms to enable data transfer
import websockets

from Exceptions.MalformedCommandException import MalformedCommandException
from User import *

class ConnectionManager:

    def __init__(self, room_count : int) -> None:

        self.users = {}      # {"user_id" : {"connection" : websocket_object, "room_id" : "1", "name" : "jimmy"}} THIS SECOND PART WILL BE HELD IN TEH USER OBJECT
                            # users = {"user_1" : {"connection" : "1", "room_id" : "2", "name" : "3"},
                            #          "user_2" : {"connection" : "4", "room_id" : "5", "name" : "6"}}

        self.rooms = {} # {"room_id" : userObj2}
        self.resetRooms(room_count) # default is 10
        
        self.prev_user_ids = list()
    
    def addToRoom(self, room_id, user_id) -> None:
        self.rooms[room_id].add(self.users[user_id])
        self.users[user_id].room_id = room_id

    # disconnect a particular user
    async def disconnectUser(self, user_id) -> None:
        self.prev_user_ids.append(user_id)
        await self.getUserConnection(user_id).close()

    async def disconnectRoom(self, room_id) -> None:
        users_to_disconnect = list(self.rooms[room_id]) # makes a copy of the items to iterate over so it doesn't adjust the end loop size
        for user in users_to_disconnect:
            await user.connection.close()

    def removeFromRoom(self, room_id, user_id) -> None:
        self.rooms[room_id].remove(self.users[user_id]) # rooms holds the user object
        self.users[user_id].room_id = "-1" # not in a room

    # the below 2 could maybe be refactored into other functions
    def checkRoomExists(self, room_id):
        try:
            targetRoom = self.rooms[room_id] # this will raise a key error if doesn't exist
        except KeyError:
            raise MalformedCommandException(f'Room {room_id} does not exist')

    def checkUserExists(self, user_id):
        try:
            target_connection = self.getUserConnection(user_id)
        except KeyError:
            raise MalformedCommandException(f'User {user_id} does not exist')

    def changeUserRoom(self, room_id_initial, room_id_final, user_id):
        self.removeFromRoom(room_id_initial, user_id)
        self.addToRoom(room_id_final, user_id)

    def cleanUpUser(self, user_id): # TODO this may result in when a new user is added it could potentially be given the same id as an existing one, need to add a log of all removed then go through this before assigning a new id based on the length of the users
        room_id = self.getUserRoom(user_id)
        self.removeFromRoom(room_id, user_id)
        self.users.pop(user_id)

    ######################################
    ## getters and setters (and resets) ## 
    ######################################

    def getUsers(self) -> dict:
        return self.users

    def getUserConnection(self, user_id) -> websockets.WebSocketServerProtocol:
        return self.users[user_id].connection
    
    def getUserRoom(self, user_id) -> str:
        return self.users[user_id].room_id
    
    def getRooms(self) -> dict:
        return self.rooms

    def resetRooms(self, room_count=10) -> None:
        for i in range (room_count):
            self.rooms[str(i+1)] = set()
    
    async def resetServer(self) -> None:
        
        # disconnecting each room, WHICH WILL THEN AUTO CLEAN UP AFTER EACH USER so no error handling required
        
        for room_id in self.rooms:
            await self.disconnectRoom(room_id)

    def getRoomMembers(self, room_id) -> set:
        return self.rooms[room_id]
    
    def getNextUserID(self) -> str:
        if len(self.prev_user_ids) == 0:
            return str(len(self.users)+1)
        
        to_assign = self.prev_user_ids[0]
        self.prev_user_ids.pop(0)
        return to_assign
    
    def getUserName(self, user_id) -> str:
        return self.users[user_id].name
    
    def setUserName(self, user_id: str, name: str) -> None:
        self.users[user_id].name = name