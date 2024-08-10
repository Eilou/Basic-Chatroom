import websockets

class User:
    def __init__(self, user_id, connection) -> None:
        self.user_id : str = user_id
        self.connection : websockets.WebSocketServerProtocol= connection
        self.room_id : str = ""
        self.name : str = ""

    