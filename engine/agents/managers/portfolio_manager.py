"""Portfolio Manager agent — final gatekeeper for trade execution."""

from __future__ import annotations

import json
import logging
from typing import Any

from engine.agents.utils.prompts import PORTFOLIO_MANAGER_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context, parse_json_from_response
from engine.agents.utils.agent_states import FinalDecision
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_portfolio_manager(
    llm: BaseLLMClient,
    pair: str,
    trade_proposal: str,
    risk_consensus: str,
    portfolio_state: dict[str, Any],
    current_stage: str,
    stage_rules: dict[str, Any],
    memory_context: list[str] | None = None,
) -> FinalDecision:
    """Run the portfolio manager to approve, modify, or reject a trade."""
    prompt = PORTFOLIO_MANAGER_PROMPT.format(
        pair=pair,
        trade_proposal=trade_proposal,
        risk_consensus=risk_consensus,
        portfolio_state=json.dumps(portfolio_state, default=str),
        current_stage=current_stage,
        stage_rules=json.dumps(stage_rules, default=str),
        memory_context=format_memory_context(memory_context or []),
    )

    response = await invoke_agent(
        llm,
        prompt,
        f"Approve or reject the trade. Output ONLY valid JSON, nothing else. stop_loss and take_profit must be single numbers.",
        temperature=0.2,
    )

    parsed = parse_json_from_response(response)
    if parsed:
        # Fix common LLM response issues
        if parsed.get("action") not in ("BUY", "SELL", "HOLD"):
            parsed["action"] = "HOLD"
        if not parsed.get("pair"):
            parsed["pair"] = pair
        if parsed.get("size_pct") is None:
            parsed["size_pct"] = 0
        if parsed.get("approved") is None:
            parsed["approved"] = False
        try:
            return FinalDecision(**parsed)
        except Exception as e:
            logger.warning(f"FinalDecision validation failed: {e}")

    # Fallback: HOLD if we can't parse
    logger.warning("Could not parse portfolio manager response, defaulting to HOLD")
    return FinalDecision(
        approved=False,
        action="HOLD",
        pair=pair,
        size_pct=0,
        reasoning=f"Failed to parse decision. Raw response: {response[:200]}",
    )
