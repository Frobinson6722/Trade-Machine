"""Bridge between FastAPI and the trading engine."""

from __future__ import annotations

import logging
from typing import Any

from engine.rules_engine import RulesEngine
from backend.services.trade_logger import TradeLogger

logger = logging.getLogger(__name__)


class EngineBridge:
    """Manages the rules engine lifecycle from the FastAPI backend."""

    def __init__(self):
        self.scheduler: RulesEngine | None = None
        self.trade_logger = TradeLogger()

    async def start(self, config: dict[str, Any] | None = None) -> None:
        """Create and start the rules-based trading engine."""
        self.scheduler = RulesEngine(
            config=config,
            on_trade=self.trade_logger.on_trade,
            on_agent_log=self.trade_logger.on_agent_log,
            on_status=self.trade_logger.on_status,
        )
        await self.scheduler.start()
        logger.info("Engine bridge: rules engine started")

    async def stop(self) -> None:
        if self.scheduler:
            await self.scheduler.stop()
            logger.info("Engine bridge: rules engine stopped")

    def get_status(self) -> dict[str, Any]:
        if not self.scheduler:
            return {"running": False, "mode": "paper", "stage": {"current_stage": "paper"}}
        return self.scheduler.get_status()
