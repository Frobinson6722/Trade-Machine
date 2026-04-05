"""Conditional edge logic for the LangGraph trading pipeline."""

from __future__ import annotations

from engine.agents.utils.agent_states import TradingCycleState


def should_continue_invest_debate(state: dict) -> str:
    """Decide whether to continue the bull/bear debate or move to research manager."""
    debate = state.get("invest_debate")
    if not debate:
        return "research_manager"

    if isinstance(debate, dict):
        round_num = debate.get("round_number", 0)
        max_rounds = debate.get("max_rounds", 2)
    else:
        round_num = debate.round_number
        max_rounds = debate.max_rounds

    if round_num >= max_rounds:
        return "research_manager"
    return "bull_researcher"


def should_execute_trade(state: dict) -> str:
    """Decide whether to proceed to risk debate or skip (HOLD)."""
    proposal = state.get("trade_proposal")
    if not proposal:
        return "end"

    action = proposal.action if hasattr(proposal, "action") else proposal.get("action", "HOLD")
    if action == "HOLD":
        return "end"
    return "risk_debate"


def should_continue_risk_debate(state: dict) -> str:
    """Decide whether to continue risk debate or move to portfolio manager."""
    debate = state.get("risk_debate")
    if not debate:
        return "portfolio_manager"

    if isinstance(debate, dict):
        round_num = debate.get("round_number", 0)
        max_rounds = debate.get("max_rounds", 2)
    else:
        round_num = debate.round_number
        max_rounds = debate.max_rounds

    if round_num >= max_rounds:
        return "portfolio_manager"
    return "aggressive_debator"


def should_execute_final(state: dict) -> str:
    """Check if portfolio manager approved the trade."""
    decision = state.get("final_decision")
    if not decision:
        return "end"

    approved = decision.approved if hasattr(decision, "approved") else decision.get("approved", False)
    if approved:
        return "execute"
    return "end"
