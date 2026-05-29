"""
FusionGuardNet – WebSocket Router
Streams real-time alerts to connected React clients.
"""

import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.packet_sniffer.sniffer import (
    register_alert_callback,
    unregister_alert_callback,
    RECENT_ALERTS,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/alerts")
async def websocket_alerts(ws: WebSocket):
    """
    On connect:
      1. Send the last 20 alerts as a 'history' message.
      2. Register a callback so every new alert is pushed immediately.
    """
    await ws.accept()
    logger.info("WebSocket client connected: %s", ws.client)

    # Send alert history on connect
    history = list(RECENT_ALERTS)[:20]
    await ws.send_text(json.dumps({"type": "history", "alerts": history}))

    # Define per-connection callback
    async def push_alert(alert: dict):
        try:
            await ws.send_text(json.dumps({"type": "alert", "alert": alert}))
        except Exception:
            pass   # disconnected

    register_alert_callback(push_alert)

    try:
        while True:
            # Keep connection alive; client can send "ping"
            data = await ws.receive_text()
            if data.strip().lower() == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected: %s", ws.client)
    finally:
        unregister_alert_callback(push_alert)
