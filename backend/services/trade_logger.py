"""Trade logger — persists engine events to DB and broadcasts via WebSocket."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TradeLogger:
    """Callback handler that persists engine events and broadcasts to WebSocket clients."""

    async def on_trade(self, trade_data: dict[str, Any]) -> None:
        """Called when a trade is executed by the engine."""
        logger.info(f"Trade executed: {trade_data}")

        # Broadcast to WebSocket clients
        from backend.routers.ws import broadcast
        await broadcast("trade_update", trade_data)

    async def on_agent_log(self, agent_name: str, content: str) -> None:
        """Called when an agent produces output during a cycle."""
        logger.debug(f"Agent log [{agent_name}]: {content[:100]}...")

        from backend.routers.ws import broadcast
        await broadcast("agent_activity", {
            "agent_name": agent_name,
            "content": content[:500],
        })

    async def on_status(self, status: str) -> None:
        """Called when the engine status changes."""
        logger.info(f"Engine status: {status}")

        from backend.routers.ws import broadcast
        await broadcast("status_change", {"status": status})
