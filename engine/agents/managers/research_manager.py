"""Research Manager agent — orchestrates bull/bear debate and produces verdict."""

from __future__ import annotations

import logging

from engine.agents.utils.prompts import RESEARCH_MANAGER_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_research_manager(
    llm: BaseLLMClient,
    pair: str,
    bull_thesis: str,
    bear_thesis: str,
    debate_history: str = "",
    memory_context: list[str] | None = None,
) -> str:
    """Run the research manager to produce a consensus research verdict."""
    prompt = RESEARCH_MANAGER_PROMPT.format(
        pair=pair,
        bull_thesis=bull_thesis,
        bear_thesis=bear_thesis,
        debate_history=debate_history,
        memory_context=format_memory_context(memory_context or []),
    )

    verdict = await invoke_agent(
        llm, prompt, "Produce your research verdict now.", temperature=0.3
    )
    logger.info(f"Research manager completed verdict for {pair}")
    return verdict
