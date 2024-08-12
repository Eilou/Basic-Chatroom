import websockets

class User:
    def __init__(self, user_id, connection) -> None:
        self.user_id : str = user_id
        self.connection : websockets.WebSocketServerProtocol= connection
        self.connection
        self.room_id : str = ""
        self.name : str = ""

    def __str__(self) -> str:
        return f'User ID: {self.user_id}, In Room: {self.room_id}, Name: {self.name}'
    