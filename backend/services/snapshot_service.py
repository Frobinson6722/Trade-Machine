"""Snapshot service — periodic portfolio snapshots for equity curve data."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import async_session
from backend.models import PortfolioSnapshot

logger = logging.getLogger(__name__)


class SnapshotService:
    """Takes periodic portfolio snapshots and persists them to the database."""

    def __init__(self, get_portfolio_fn):
        self.get_portfolio = get_portfolio_fn
        self._task: asyncio.Task | None = None
        self.running = False

    async def start(self, interval_seconds: int = 60) -> None:
        """Start taking periodic snapshots."""
        self.running = True
        self._task = asyncio.create_task(self._loop(interval_seconds))

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()

    async def _loop(self, interval: int) -> None:
        while self.running:
            try:
                await self._take_snapshot()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Snapshot error: {e}")
                await asyncio.sleep(interval)

    async def _take_snapshot(self) -> None:
        """Take a single portfolio snapshot and persist it."""
        try:
            portfolio = self.get_portfolio()
            if not portfolio:
                return

            async with async_session() as session:
                snapshot = PortfolioSnapshot(
                    timestamp=datetime.now(timezone.utc),
                    total_value=portfolio.get("total_value", 0),
                    cash_balance=portfolio.get("cash_balance", 0),
                    positions_value=portfolio.get("positions_value", 0),
                    unrealized_pnl=portfolio.get("unrealized_pnl", 0),
                    realized_pnl_cumulative=portfolio.get("realized_pnl", 0),
                )
                session.add(snapshot)
                await session.commit()

        except Exception as e:
            logger.error(f"Failed to take snapshot: {e}")
