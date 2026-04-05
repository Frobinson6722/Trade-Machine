"""Signal processing — extracts and validates structured trade signals from LLM output."""

from __future__ import annotations

import logging
from typing import Any

from engine.agents.utils.agent_states import TradeSignal, FinalDecision

logger = logging.getLogger(__name__)


def validate_trade_signal(signal: TradeSignal, stage_limits: dict[str, Any]) -> TradeSignal:
    """Validate and clamp a trade signal to stage-appropriate limits."""
    max_size = stage_limits.get("max_position_size_pct", 5.0)

    if signal.size_pct > max_size:
        logger.info(f"Clamping position size from {signal.size_pct}% to {max_size}%")
        signal.size_pct = max_size

    if signal.confidence < 0:
        signal.confidence = 0
    elif signal.confidence > 1:
        signal.confidence = 1

    return signal


def validate_final_decision(
    decision: FinalDecision, stage: str, stage_config: dict[str, Any]
) -> FinalDecision:
    """Enforce stage-specific constraints on the final decision."""
    if stage == "micro":
        max_usd = stage_config.get("trade_size_usd", 1.0)
        # Size will be enforced at execution time based on USD amount
        logger.info(f"Micro stage: trade will be capped at ${max_usd}")

    elif stage == "graduated":
        sizes = stage_config.get("sizes_usd", [2.0, 5.0, 10.0])
        logger.info(f"Graduated stage: available sizes ${sizes}")

    return decision


def compute_risk_reward_ratio(
    entry_price: float,
    stop_loss: float | None,
    take_profit: float | None,
    action: str,
) -> float | None:
    """Compute risk/reward ratio for a trade setup."""
    if not stop_loss or not take_profit or entry_price <= 0:
        return None

    if action == "BUY":
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
    else:  # SELL
        risk = abs(stop_loss - entry_price)
        reward = abs(entry_price - take_profit)

    if risk == 0:
        return None
    return round(reward / risk, 2)
