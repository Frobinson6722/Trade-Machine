"""Trader agent — converts research verdict into concrete trade proposals."""

from __future__ import annotations

import json
import logging
from typing import Any

from engine.agents.utils.prompts import TRADER_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context, parse_json_from_response
from engine.agents.utils.agent_states import TradeSignal
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_trader(
    llm: BaseLLMClient,
    pair: str,
    research_verdict: str,
    current_positions: dict[str, Any],
    account_balance: float,
    current_stage: str,
    max_position_size_pct: float,
    memory_context: list[str] | None = None,
) -> TradeSignal:
    """Run the trader agent to produce a concrete trade proposal."""
    prompt = TRADER_PROMPT.format(
        pair=pair,
        research_verdict=research_verdict,
        current_positions=json.dumps(current_positions, default=str),
        account_balance=f"${account_balance:,.2f}",
        current_stage=current_stage,
        max_position_size_pct=max_position_size_pct,
        memory_context=format_memory_context(memory_context or []),
    )

    response = await invoke_agent(
        llm,
        prompt,
        """Produce your trade proposal. Respond with JSON:
{
    "action": "BUY"|"SELL"|"HOLD",
    "pair": "...",
    "size_pct": ...,
    "entry_type": "market"|"limit",
    "limit_price": null,
    "stop_loss": ...,
    "take_profit": ...,
    "confidence": 0.0-1.0,
    "reasoning": "your reasoning"
}""",
        temperature=0.3,
    )

    parsed = parse_json_from_response(response)
    if parsed:
        # Fix common LLM response issues
        if not parsed.get("entry_type") or parsed["entry_type"] not in ("market", "limit"):
            parsed["entry_type"] = "market"
        if parsed.get("confidence") is None:
            parsed["confidence"] = 0.5
        if parsed.get("size_pct") is None:
            parsed["size_pct"] = 0
        if parsed.get("action") not in ("BUY", "SELL", "HOLD"):
            parsed["action"] = "HOLD"
        if not parsed.get("pair"):
            parsed["pair"] = pair

        # Handle take_profit/stop_loss as list (Claude sometimes returns multiple levels)
        tp = parsed.get("take_profit")
        if isinstance(tp, list):
            parsed["take_profit"] = tp[0]["level"] if tp and isinstance(tp[0], dict) and "level" in tp[0] else tp[0] if tp else None
        elif tp is not None:
            try:
                parsed["take_profit"] = float(tp)
            except (ValueError, TypeError):
                parsed["take_profit"] = None

        sl = parsed.get("stop_loss")
        if isinstance(sl, list):
            parsed["stop_loss"] = sl[0]["level"] if sl and isinstance(sl[0], dict) and "level" in sl[0] else sl[0] if sl else None
        elif sl is not None:
            try:
                parsed["stop_loss"] = float(sl)
            except (ValueError, TypeError):
                parsed["stop_loss"] = None

        # Handle limit_price
        lp = parsed.get("limit_price")
        if lp is not None:
            try:
                parsed["limit_price"] = float(lp)
            except (ValueError, TypeError):
                parsed["limit_price"] = None

        try:
            return TradeSignal(**parsed)
        except Exception as e:
            logger.warning(f"TradeSignal validation failed: {e}")
            pass

    # Fallback: HOLD if we can't parse
    logger.warning("Could not parse trader response, defaulting to HOLD")
    return TradeSignal(
        action="HOLD",
        pair=pair,
        size_pct=0,
        confidence=0,
        reasoning=f"Failed to parse trade proposal. Raw: {response[:200]}",
    )
