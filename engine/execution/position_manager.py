"""Position manager — tracks open positions and monitors stop/take-profit levels."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PositionManager:
    """Tracks positions across all trading pairs and calculates P&L."""

    def __init__(self):
        self.positions: dict[str, dict[str, Any]] = {}

    def update_position(self, pair: str, position: dict[str, Any]) -> None:
        """Add or update a tracked position."""
        self.positions[pair] = position
        logger.debug(f"Position updated for {pair}: {position}")

    def close_position(self, pair: str) -> dict[str, Any] | None:
        """Remove a tracked position and return it."""
        return self.positions.pop(pair, None)

    def get_position(self, pair: str) -> dict[str, Any] | None:
        return self.positions.get(pair)

    def get_all_positions(self) -> dict[str, dict[str, Any]]:
        return dict(self.positions)

    def calculate_unrealized_pnl(self, prices: dict[str, float]) -> dict[str, Any]:
        """Calculate unrealized P&L for all open positions."""
        results = {}
        total_pnl = 0.0

        for pair, pos in self.positions.items():
            current_price = prices.get(pair, pos.get("entry_price", 0))
            entry_price = pos.get("entry_price", 0)
            quantity = pos.get("quantity", 0)
            side = pos.get("side", "long")

            if side == "long":
                pnl = (current_price - entry_price) * quantity
            else:
                pnl = (entry_price - current_price) * quantity

            pnl_pct = ((current_price / entry_price) - 1) * 100 if entry_price else 0
            if side == "short":
                pnl_pct = -pnl_pct

            results[pair] = {
                "entry_price": entry_price,
                "current_price": current_price,
                "quantity": quantity,
                "unrealized_pnl": pnl,
                "unrealized_pnl_pct": pnl_pct,
            }
            total_pnl += pnl

        return {"positions": results, "total_unrealized_pnl": total_pnl}

    def check_stops(self, prices: dict[str, float]) -> list[dict[str, Any]]:
        """Check all positions for stop-loss/take-profit triggers."""
        triggered = []
        for pair, pos in list(self.positions.items()):
            current_price = prices.get(pair)
            if not current_price:
                continue

            sl = pos.get("stop_loss")
            tp = pos.get("take_profit")

            if sl and current_price <= sl:
                triggered.append({"pair": pair, "trigger": "stop_loss", "price": current_price})
            elif tp and current_price >= tp:
                triggered.append({"pair": pair, "trigger": "take_profit", "price": current_price})

        return triggered
