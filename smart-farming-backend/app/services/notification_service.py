from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    """Tracks live WebSocket connections per farm_id so we can push updates."""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, farm_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(farm_id, []).append(websocket)

    def disconnect(self, farm_id: int, websocket: WebSocket):
        if farm_id in self.active_connections:
            self.active_connections[farm_id].remove(websocket)
            if not self.active_connections[farm_id]:
                del self.active_connections[farm_id]

    async def broadcast(self, farm_id: int, message: dict):
        for connection in self.active_connections.get(farm_id, []):
            await connection.send_json(message)


manager = ConnectionManager()
