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
        return TradeSignal(**parsed)

    # Fallback: HOLD if we can't parse
    logger.warning("Could not parse trader response, defaulting to HOLD")
    return TradeSignal(
        action="HOLD",
        pair=pair,
        size_pct=0,
        confidence=0,
        reasoning=f"Failed to parse trade proposal. Raw: {response[:200]}",
    )
