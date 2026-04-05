"""Trade logger — persists engine events to DB and broadcasts via WebSocket."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update

logger = logging.getLogger(__name__)


class TradeLogger:
    """Callback handler that persists engine events to DB and broadcasts via WebSocket."""

    async def on_trade(self, trade_data: dict[str, Any]) -> None:
        """Called when a trade is executed by the engine. Persists to DB."""
        logger.info(f"Trade executed: {trade_data}")

        action = trade_data.get("action", "BUY")

        try:
            from backend.database import async_session
            from backend.models import Trade

            async with async_session() as session:
                if action == "BUY":
                    trade = Trade(
                        cycle_id=trade_data.get("cycle_id", ""),
                        pair=trade_data.get("pair", ""),
                        side="BUY",
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
                    logger.info(f"BUY trade persisted: {trade.cycle_id}")

                elif action == "SELL":
                    # Close the matching open trade by cycle_id
                    cycle_id = trade_data.get("cycle_id", "")
                    pair = trade_data.get("pair", "")
                    pnl = trade_data.get("pnl", 0)
                    pnl_pct = trade_data.get("pnl_pct", 0)
                    exit_price = trade_data.get("price", 0)
                    trigger = trade_data.get("trigger", "manual")

                    # Try to find by cycle_id first, then by pair
                    result = await session.execute(
                        select(Trade).where(
                            Trade.cycle_id == cycle_id,
                            Trade.status == "open"
                        )
                    )
                    trade = result.scalar_one_or_none()

                    if not trade:
                        # Fallback: close the most recent open trade for this pair
                        result = await session.execute(
                            select(Trade).where(
                                Trade.pair == pair,
                                Trade.status == "open"
                            ).order_by(Trade.opened_at.desc())
                        )
                        trade = result.scalar_one_or_none()

                    if trade:
                        trade.status = "closed"
                        trade.exit_price = exit_price
                        trade.pnl = pnl
                        trade.pnl_pct = pnl_pct
                        trade.exit_trigger = trigger
                        trade.closed_at = datetime.now(timezone.utc)
                        await session.commit()
                        logger.info(f"Trade closed: {pair} P&L: ${pnl:+.2f} ({trigger})")
                    else:
                        logger.warning(f"No open trade found to close for {pair} cycle {cycle_id}")

        except Exception as e:
            logger.error(f"Failed to persist trade: {e}")

        # Broadcast to WebSocket clients
        from backend.routers.ws import broadcast
        await broadcast("trade_update", trade_data)

    async def on_agent_log(self, agent_name: str, content: str) -> None:
        """Called when an agent produces output during a cycle. Persists to DB."""
        logger.debug(f"Agent log [{agent_name}]: {content[:100]}...")

        try:
            from backend.database import async_session
            from backend.models import AgentLog

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
                    cycle_id="",
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

        # On startup, close any stale open trades from previous sessions
        if status == "running":
            await self._close_stale_trades()

        from backend.routers.ws import broadcast
        await broadcast("status_change", {"status": status})

    async def _close_stale_trades(self) -> None:
        """Close any trades left open from a previous engine session."""
        try:
            from backend.database import async_session
            from backend.models import Trade

            async with async_session() as session:
                result = await session.execute(
                    select(Trade).where(Trade.status == "open")
                )
                stale_trades = result.scalars().all()

                if stale_trades:
                    logger.info(f"Closing {len(stale_trades)} stale trades from previous session")
                    for trade in stale_trades:
                        trade.status = "closed"
                        trade.exit_price = trade.entry_price  # Close at entry (no P&L data)
                        trade.pnl = 0
                        trade.pnl_pct = 0
                        trade.exit_trigger = "session_restart"
                        trade.closed_at = datetime.now(timezone.utc)
                    await session.commit()
        except Exception as e:
            logger.error(f"Failed to close stale trades: {e}")
