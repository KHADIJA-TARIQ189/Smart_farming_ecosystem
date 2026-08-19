from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.notification_service import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/farm/{farm_id}")
async def farm_live_feed(websocket: WebSocket, farm_id: int):
    """
    Frontend dashboard connects here to receive live sensor readings and alerts
    for a given farm, pushed via manager.broadcast() from the ingest endpoint
    or the MQTT service.
    """
    await manager.connect(farm_id, websocket)
    try:
        while True:
            # Keep the connection open; we don't expect incoming messages from
            # the dashboard, but reading keeps the socket alive and detects disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(farm_id, websocket)
