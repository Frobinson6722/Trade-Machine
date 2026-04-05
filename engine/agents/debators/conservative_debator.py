"""Conservative Risk Debator — argues for capital preservation and tighter risk controls."""

from __future__ import annotations

import logging

from engine.agents.utils.prompts import CONSERVATIVE_DEBATOR_PROMPT
from engine.agents.utils.agent_utils import invoke_agent
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_conservative_debator(
    llm: BaseLLMClient,
    pair: str,
    trade_proposal: str,
) -> str:
    """Run the conservative risk debator on a trade proposal."""
    prompt = CONSERVATIVE_DEBATOR_PROMPT.format(
        pair=pair,
        trade_proposal=trade_proposal,
    )

    result = await invoke_agent(
        llm, prompt, "Argue for more conservative positioning.", temperature=0.5
    )
    logger.info(f"Conservative debator completed for {pair}")
    return result
