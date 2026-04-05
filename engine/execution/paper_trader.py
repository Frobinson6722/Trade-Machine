"""Paper trading simulator — tracks virtual balances and simulates fills."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class PaperTrader:
    """In-memory paper trading simulator."""

    def __init__(self, initial_balance: float = 10000.0):
        self.cash_balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: dict[str, dict[str, Any]] = {}
        self.trade_history: list[dict[str, Any]] = []

    async def place_order(
        self,
        pair: str,
        side: str,
        size_usd: float,
        current_price: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> dict[str, Any]:
        """Simulate placing an order at the current market price."""
        order_id = str(uuid.uuid4())[:8]

        if side == "BUY":
            if size_usd > self.cash_balance:
                size_usd = self.cash_balance
                logger.warning(f"Insufficient balance, capping order to ${size_usd:.2f}")

            if size_usd <= 0:
                return {"success": False, "reason": "Insufficient balance"}

            quantity = size_usd / current_price
            self.cash_balance -= size_usd

            self.positions[pair] = {
                "order_id": order_id,
                "pair": pair,
                "side": "long",
                "entry_price": current_price,
                "quantity": quantity,
                "size_usd": size_usd,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "opened_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"[PAPER] BUY {pair}: {quantity:.6f} @ ${current_price:,.2f} (${size_usd:.2f})")

        elif side == "SELL":
            if pair not in self.positions:
                return {"success": False, "reason": f"No open position for {pair}"}

            pos = self.positions.pop(pair)
            pnl = (current_price - pos["entry_price"]) * pos["quantity"]
            pnl_pct = ((current_price / pos["entry_price"]) - 1) * 100
            self.cash_balance += pos["size_usd"] + pnl

            trade_record = {
                "order_id": order_id,
                "pair": pair,
                "side": "SELL",
                "entry_price": pos["entry_price"],
                "exit_price": current_price,
                "quantity": pos["quantity"],
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "opened_at": pos["opened_at"],
                "closed_at": datetime.now(timezone.utc).isoformat(),
            }
            self.trade_history.append(trade_record)

            logger.info(f"[PAPER] SELL {pair}: {pos['quantity']:.6f} @ ${current_price:,.2f} (P&L: ${pnl:+,.2f})")
            return {"success": True, "trade": trade_record}

        return {
            "success": True,
            "order_id": order_id,
            "pair": pair,
            "side": side,
            "price": current_price,
            "size_usd": size_usd,
        }

    async def check_stops(self, pair: str, current_price: float) -> dict[str, Any] | None:
        """Check if any stop-loss or take-profit has been hit."""
        if pair not in self.positions:
            return None

        pos = self.positions[pair]
        triggered = None

        if pos["stop_loss"] and current_price <= pos["stop_loss"]:
            triggered = "stop_loss"
        elif pos["take_profit"] and current_price >= pos["take_profit"]:
            triggered = "take_profit"

        if triggered:
            logger.info(f"[PAPER] {triggered.upper()} triggered for {pair} @ ${current_price:,.2f}")
            return await self.place_order(pair, "SELL", 0, current_price)

        return None

    def get_portfolio_value(self, prices: dict[str, float]) -> float:
        """Calculate total portfolio value including open positions."""
        total = self.cash_balance
        for pair, pos in self.positions.items():
            price = prices.get(pair, pos["entry_price"])
            total += pos["quantity"] * price
        return total

    def get_positions(self) -> dict[str, dict[str, Any]]:
        return dict(self.positions)

    def get_stats(self) -> dict[str, Any]:
        """Calculate trading statistics."""
        if not self.trade_history:
            return {"total_trades": 0, "win_rate": 0, "total_pnl": 0}

        wins = sum(1 for t in self.trade_history if t["pnl"] > 0)
        total_pnl = sum(t["pnl"] for t in self.trade_history)

        return {
            "total_trades": len(self.trade_history),
            "wins": wins,
            "losses": len(self.trade_history) - wins,
            "win_rate": wins / len(self.trade_history),
            "total_pnl": total_pnl,
            "avg_pnl": total_pnl / len(self.trade_history),
        }
