"""WebSocket endpoint for real-time dashboard updates."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

# Connected WebSocket clients
connected_clients: set[WebSocket] = set()


async def broadcast(message_type: str, data: dict[str, Any]) -> None:
    """Broadcast a message to all connected WebSocket clients."""
    if not connected_clients:
        return

    payload = json.dumps({"type": message_type, "data": data})
    disconnected = set()

    for ws in connected_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)

    connected_clients.difference_update(disconnected)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time updates.

    Pushes: trade_update, agent_activity, pnl_tick, status_change
    """
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(connected_clients)}")

    try:
        # Send initial status
        bridge = websocket.app.state.engine_bridge
        status = bridge.get_status()
        await websocket.send_text(json.dumps({
            "type": "status_change",
            "data": status,
        }))

        # Keep connection alive, handle pings
        while True:
            # TEST MODE: heartbeat timer disabled (kept for test mode)
            # try:
            #     data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            #     if data == "ping":
            #         await websocket.send_text(json.dumps({"type": "pong"}))
            # except asyncio.TimeoutError:
            #     await websocket.send_text(json.dumps({"type": "heartbeat"}))
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(connected_clients)}")
