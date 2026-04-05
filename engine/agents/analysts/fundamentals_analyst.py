"""Fundamentals Analyst agent — on-chain data and token metrics."""

from __future__ import annotations

import logging
from typing import Any

from engine.agents.utils.prompts import FUNDAMENTALS_ANALYST_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context, format_data_for_prompt
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_fundamentals_analyst(
    llm: BaseLLMClient,
    pair: str,
    onchain_data: dict[str, Any],
    memory_context: list[str] | None = None,
) -> str:
    """Run the fundamentals analyst agent on on-chain data."""
    prompt = FUNDAMENTALS_ANALYST_PROMPT.format(
        pair=pair,
        memory_context=format_memory_context(memory_context or []),
    )

    user_content = f"""Analyze on-chain fundamentals for {pair}:

## On-Chain Metrics
{format_data_for_prompt(onchain_data)}

Provide your structured fundamental analysis."""

    report = await invoke_agent(llm, prompt, user_content, temperature=0.3)
    logger.info(f"Fundamentals analyst completed analysis for {pair}")
    return report
