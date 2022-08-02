from typing import List
from fastapi import WebSocket
from random import randint

class ConnectionManager:
    def __init__(self):
        self.user_move = []
        self.connections = []
        
        
    def get_user_life(self, websocket: WebSocket):
        return [connection['life'] for connection in self.connections if connection['websocket'] == websocket][0]

    async def connect(self, websocket: WebSocket):
        if len(self.connections) >= 2:
            await websocket.accept()
            await websocket.close(4000)
        await websocket.accept()
        self.connections.append({'websocket': websocket, 'life': 100})
        
        await websocket.send_json({
                'life': self.get_user_life(websocket)
            })
        
        if len(self.connections) == 1:
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
            await self.connections[0]['websocket'].send_json({
                "init": True,
                "message": "Second player is ready",
                "player": 1
            })

    async def disconnect(self, websocket: WebSocket):
        try:
            self.connections.pop([self.connections.index(i) for i in self.connections if i['websocket'] == websocket][0])
            await websocket.close(4000)
        except:
            pass

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection['websocket'].send_json(data)
            
            
    async def minus_lifes(self, websocket: WebSocket):

        self.connections[[self.connections.index(i) for i in self.connections if i['websocket'] == websocket][0]]['life'] -= randint(10,20)
        
        await self.connections[0]['websocket'].send_json({
                'life': self.get_user_life(self.connections[0]['websocket'])
            })
        await self.connections[1]['websocket'].send_json({
                'life': self.get_user_life(self.connections[1]['websocket'])
            })
        
    async def win_lose(self):
        
        if self.get_user_life(self.connections[1]['websocket']) <= 0:
            await self.connections[1]['websocket'].send_json({
                "message": "You are lose :(",
            })
            await self.connections[0]['websocket'].send_json({
                "message": "You are win :)",
            })
            
            await self.disconnect(self.connections[1]['websocket'])
            await self.disconnect(self.connections[0]['websocket'])
            
        elif self.get_user_life(self.connections[0]['websocket']) <= 0:
            await self.connections[0]['websocket'].send_json({
                "message": "You are lose :(",
            })
            await self.connections[1]['websocket'].send_json({
                "message": "You are win :)",
            })
            
            await self.disconnect(self.connections[1]['websocket'])
            await self.disconnect(self.connections[0]['websocket'])
            
