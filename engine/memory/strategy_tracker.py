"""Strategy tracker — records strategy evolution over time."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class StrategyTracker:
    """Tracks all strategy changes and their impact on performance."""

    def __init__(self):
        self.updates: list[dict[str, Any]] = []
        self.current_parameters: dict[str, Any] = {
            "min_confidence": 0.6,
            "max_position_size_pct": 5.0,
            "default_stop_loss_pct": 3.0,
            "default_take_profit_pct": 6.0,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "min_risk_reward_ratio": 1.5,
            "sentiment_weight": 0.2,
            "technical_weight": 0.4,
            "news_weight": 0.2,
            "fundamental_weight": 0.2,
        }

    def record_update(
        self,
        description: str,
        parameter_changes: dict[str, Any],
        trigger_trade_id: str | None = None,
        performance_before: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record a strategy update with before/after context."""
        old_values = {}
        for key, new_val in parameter_changes.items():
            old_values[key] = self.current_parameters.get(key)
            self.current_parameters[key] = new_val

        entry = {
            "id": len(self.updates),
            "description": description,
            "parameter_changes": parameter_changes,
            "old_values": old_values,
            "trigger_trade_id": trigger_trade_id,
            "performance_before": performance_before,
            "performance_after": None,  # Filled in later
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.updates.append(entry)
        logger.info(f"Strategy update: {description}")
        return entry

    def update_performance_after(
        self, update_id: int, performance: dict[str, Any]
    ) -> None:
        """Record performance metrics after a strategy change took effect."""
        if update_id < len(self.updates):
            self.updates[update_id]["performance_after"] = performance

    def get_current_parameters(self) -> dict[str, Any]:
        return dict(self.current_parameters)

    def get_updates(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.updates[-limit:]

    def get_parameter_history(self, parameter: str) -> list[dict[str, Any]]:
        """Get the change history for a specific parameter."""
        history = []
        for update in self.updates:
            if parameter in update["parameter_changes"]:
                history.append({
                    "old_value": update["old_values"].get(parameter),
                    "new_value": update["parameter_changes"][parameter],
                    "description": update["description"],
                    "timestamp": update["created_at"],
                })
        return history
