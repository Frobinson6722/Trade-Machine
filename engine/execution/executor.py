"""Order executor — routes trades to paper or live trader based on current stage."""

from __future__ import annotations

import logging
from typing import Any

from engine.execution.paper_trader import PaperTrader
from engine.execution.live_trader import LiveTrader
from engine.agents.utils.agent_states import FinalDecision

logger = logging.getLogger(__name__)


class OrderExecutor:
    """Routes order execution to paper or live trader."""

    def __init__(
        self,
        paper_trader: PaperTrader,
        live_trader: LiveTrader | None = None,
    ):
        self.paper_trader = paper_trader
        self.live_trader = live_trader
        self.mode = "paper"  # "paper" or "live"

    def set_mode(self, mode: str) -> None:
        if mode not in ("paper", "live"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'paper' or 'live'")
        if mode == "live" and not self.live_trader:
            raise ValueError("Cannot switch to live mode: no live trader configured")
        self.mode = mode
        logger.info(f"Execution mode set to: {mode}")

    async def execute(
        self,
        decision: FinalDecision,
        current_price: float,
        account_balance: float,
        stage_trade_size: float | None = None,
    ) -> dict[str, Any]:
        """Execute a trade based on the final decision.

        Args:
            decision: The approved trade decision
            current_price: Current market price
            account_balance: Current account balance
            stage_trade_size: Fixed trade size for micro/graduated stages (USD)
        """
        if not decision.approved or decision.action == "HOLD":
            return {"executed": False, "reason": "HOLD or not approved"}

        # Calculate trade size
        if stage_trade_size is not None:
            size_usd = stage_trade_size
        else:
            size_usd = account_balance * (decision.size_pct / 100)

        if size_usd <= 0:
            return {"executed": False, "reason": "Trade size is zero"}

        trader = self.live_trader if self.mode == "live" else self.paper_trader

        result = await trader.place_order(
            pair=decision.pair,
            side=decision.action,
            size_usd=size_usd,
            current_price=current_price,
            stop_loss=decision.stop_loss,
            take_profit=decision.take_profit,
        )

        result["mode"] = self.mode
        result["executed"] = result.get("success", False)
        return result

    async def check_stops(self, pair: str, current_price: float) -> dict[str, Any] | None:
        """Check stop-loss/take-profit triggers (paper mode only for now)."""
        if self.mode == "paper":
            return await self.paper_trader.check_stops(pair, current_price)
        # Live stop monitoring would use Robinhood's built-in stops
        return None

    def get_portfolio_value(self, prices: dict[str, float]) -> float:
        if self.mode == "paper":
            return self.paper_trader.get_portfolio_value(prices)
        return 0  # Live portfolio value comes from Robinhood

    def get_positions(self) -> dict[str, dict[str, Any]]:
        if self.mode == "paper":
            return self.paper_trader.get_positions()
        return {}

    def get_stats(self) -> dict[str, Any]:
        if self.mode == "paper":
            return self.paper_trader.get_stats()
        return {"total_trades": len(self.live_trader.trade_history) if self.live_trader else 0}
