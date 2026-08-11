"""
Simple in-memory websocket manager, keyed by chat_id.
Good enough for a single backend instance. If you scale to multiple
Render instances later, swap this for a pub/sub backed approach
(e.g. Redis, or Firestore onSnapshot listeners driving pushes instead).
"""
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(chat_id, []).append(websocket)

    def disconnect(self, chat_id: str, websocket: WebSocket):
        if chat_id in self.active and websocket in self.active[chat_id]:
            self.active[chat_id].remove(websocket)
            if not self.active[chat_id]:
                del self.active[chat_id]

    async def broadcast(self, chat_id: str, message: dict):
        for connection in self.active.get(chat_id, []):
            await connection.send_json(message)


manager = ConnectionManager()
