from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ WebSocket Connected | Connection ID (User): {user_id}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            json_compatible_data = jsonable_encoder(message)
            await websocket.send_json(json_compatible_data)
            print(f"📩 Message emitted to Connection ID: {user_id}")
        else:
            print(f"⚠️ Failed to emit: Connection ID {user_id} is offline.")

manager = ConnectionManager()