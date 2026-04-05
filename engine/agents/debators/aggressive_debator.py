"""Aggressive Risk Debator — argues for larger positions and wider stops."""

from __future__ import annotations

import logging

from engine.agents.utils.prompts import AGGRESSIVE_DEBATOR_PROMPT
from engine.agents.utils.agent_utils import invoke_agent
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_aggressive_debator(
    llm: BaseLLMClient,
    pair: str,
    trade_proposal: str,
) -> str:
    """Run the aggressive risk debator on a trade proposal."""
    prompt = AGGRESSIVE_DEBATOR_PROMPT.format(
        pair=pair,
        trade_proposal=trade_proposal,
    )

    result = await invoke_agent(
        llm, prompt, "Argue for more aggressive positioning.", temperature=0.5
    )
    logger.info(f"Aggressive debator completed for {pair}")
    return result
