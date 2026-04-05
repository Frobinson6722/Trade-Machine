"""Trade logger — persists engine events to DB and broadcasts via WebSocket."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class TradeLogger:
    """Callback handler that persists engine events to DB and broadcasts via WebSocket."""

    async def on_trade(self, trade_data: dict[str, Any]) -> None:
        """Called when a trade is executed by the engine. Persists to DB."""
        logger.info(f"Trade executed: {trade_data}")

        # Persist to database
        try:
            from backend.database import async_session
            from backend.models import Trade

            async with async_session() as session:
                trade = Trade(
                    cycle_id=trade_data.get("cycle_id", ""),
                    pair=trade_data.get("pair", ""),
                    side=trade_data.get("action", "BUY"),
                    size_usd=trade_data.get("size_usd", 0),
                    entry_price=trade_data.get("price", 0),
                    stop_loss=trade_data.get("stop_loss"),
                    take_profit=trade_data.get("take_profit"),
                    status="open",
                    stage=trade_data.get("stage", "paper"),
                    mode=trade_data.get("mode", "paper"),
                    opened_at=datetime.now(timezone.utc),
                )
                session.add(trade)
                await session.commit()
                logger.info(f"Trade persisted to DB: {trade.cycle_id}")
        except Exception as e:
            logger.error(f"Failed to persist trade: {e}")

        # Broadcast to WebSocket clients
        from backend.routers.ws import broadcast
        await broadcast("trade_update", trade_data)

    async def on_agent_log(self, agent_name: str, content: str) -> None:
        """Called when an agent produces output during a cycle. Persists to DB."""
        logger.debug(f"Agent log [{agent_name}]: {content[:100]}...")

        # Persist to database
        try:
            from backend.database import async_session
            from backend.models import AgentLog

            # Classify agent type
            agent_type = "analyst"
            n = agent_name.lower()
            if "researcher" in n or "research" in n:
                agent_type = "researcher"
            elif "debat" in n:
                agent_type = "debator"
            elif "manager" in n:
                agent_type = "manager"
            elif "trader" in n:
                agent_type = "trader"

            async with async_session() as session:
                log = AgentLog(
                    cycle_id="",  # Will be set when we have cycle context
                    agent_name=agent_name,
                    agent_type=agent_type,
                    content=content,
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to persist agent log: {e}")

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
