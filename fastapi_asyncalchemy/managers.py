from typing import List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_move = []
        self.user_lifes = []
        # self.connections = []

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) >= 2:
            await websocket.accept()
            await websocket.close(4000)
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_lifes.append({'websocket': websocket, 'life': 100})
        if len(self.active_connections) == 1:
            await websocket.send_json({
                "init": True,
                "message": "Your are first player",
                "player": 1
            })
        else:
            await websocket.send_json({
                "init": True,
                "message": "Your are second player",
                "player": 2
            })
            await self.active_connections[0].send_json({
                "init": True,
                "message": "Second player is ready",
                "player": 1
            })

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            await connection.send_json(data)
            
            

