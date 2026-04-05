"""Post-trade reflection — feeds outcomes back to agent memories."""

from __future__ import annotations

import logging
from typing import Any

from engine.agents.utils.prompts import REFLECTION_PROMPT, HYPOTHESIS_PROMPT
from engine.agents.utils.agent_utils import invoke_agent
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def reflect_on_trade(
    llm: BaseLLMClient,
    pair: str,
    action: str,
    entry_price: float,
    exit_price: float,
    pnl: float,
    pnl_pct: float,
    duration: str,
    agent_reasoning: str,
    market_conditions: str,
) -> str:
    """Run the reflection process on a completed trade."""
    prompt = REFLECTION_PROMPT.format(
        pair=pair,
        action=action,
        entry_price=f"${entry_price:,.2f}",
        exit_price=f"${exit_price:,.2f}",
        pnl=f"${pnl:,.2f}",
        pnl_pct=f"{pnl_pct:+.2f}",
        duration=duration,
        agent_reasoning=agent_reasoning,
        market_conditions=market_conditions,
    )

    reflection = await invoke_agent(
        llm, prompt, "Reflect on this trade now.", temperature=0.4
    )
    logger.info(f"Reflection completed for {pair} trade (P&L: {pnl_pct:+.2f}%)")
    return reflection


async def generate_hypotheses(
    llm: BaseLLMClient,
    pair: str,
    action: str,
    entry_price: float,
    exit_price: float,
    pnl: float,
    pnl_pct: float,
    agent_reasoning: str,
) -> str:
    """Generate testable hypotheses for a losing trade."""
    prompt = HYPOTHESIS_PROMPT.format(
        pair=pair,
        action=action,
        entry_price=f"${entry_price:,.2f}",
        exit_price=f"${exit_price:,.2f}",
        pnl=f"${pnl:,.2f}",
        pnl_pct=f"{pnl_pct:+.2f}",
        agent_reasoning=agent_reasoning,
    )

    hypotheses = await invoke_agent(
        llm, prompt, "Generate your hypotheses now.", temperature=0.5
    )
    logger.info(f"Hypotheses generated for losing {pair} trade")
    return hypotheses
