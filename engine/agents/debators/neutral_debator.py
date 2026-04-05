"""Neutral Risk Debator — moderates between aggressive and conservative views."""

from __future__ import annotations

import logging

from engine.agents.utils.prompts import NEUTRAL_DEBATOR_PROMPT
from engine.agents.utils.agent_utils import invoke_agent
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_neutral_debator(
    llm: BaseLLMClient,
    pair: str,
    trade_proposal: str,
    aggressive_view: str,
    conservative_view: str,
) -> str:
    """Run the neutral debator to synthesize the risk debate."""
    prompt = NEUTRAL_DEBATOR_PROMPT.format(
        pair=pair,
        trade_proposal=trade_proposal,
        aggressive_view=aggressive_view,
        conservative_view=conservative_view,
    )

    result = await invoke_agent(
        llm, prompt, "Synthesize both perspectives into a balanced recommendation.", temperature=0.4
    )
    logger.info(f"Neutral debator completed for {pair}")
    return result
