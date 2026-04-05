"""StateGraph construction — wires all agents into the LangGraph pipeline."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from langgraph.graph import StateGraph, END

from engine.agents.analysts.market_analyst import run_market_analyst
from engine.agents.analysts.news_analyst import run_news_analyst
from engine.agents.analysts.sentiment_analyst import run_sentiment_analyst
from engine.agents.analysts.fundamentals_analyst import run_fundamentals_analyst
from engine.agents.researchers.bull_researcher import run_bull_researcher
from engine.agents.researchers.bear_researcher import run_bear_researcher
from engine.agents.managers.research_manager import run_research_manager
from engine.agents.trader.trader import run_trader
from engine.agents.debators.aggressive_debator import run_aggressive_debator
from engine.agents.debators.conservative_debator import run_conservative_debator
from engine.agents.debators.neutral_debator import run_neutral_debator
from engine.agents.managers.portfolio_manager import run_portfolio_manager
from engine.graph.conditional_logic import (
    should_continue_invest_debate,
    should_execute_trade,
    should_continue_risk_debate,
    should_execute_final,
)
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


def build_trading_graph(
    llm: BaseLLMClient,
    deep_llm: BaseLLMClient,
    config: dict[str, Any],
) -> StateGraph:
    """Build and compile the full trading pipeline as a LangGraph StateGraph."""

    graph = StateGraph(dict)

    # --- Analyst nodes (run in parallel) ---
    async def analyst_node(state: dict) -> dict:
        pair = state["pair"]
        memory = state.get("similar_past_trades", [])

        # Run all 4 analysts concurrently
        market_task = run_market_analyst(
            llm, pair, state.get("market_data", {}),
            state.get("market_data", {}).get("indicators", {}), memory
        )
        news_task = run_news_analyst(llm, pair, state.get("news_data", []), memory)
        sentiment_task = run_sentiment_analyst(llm, pair, state.get("sentiment_data", {}), memory)
        fundamentals_task = run_fundamentals_analyst(llm, pair, state.get("onchain_data", {}), memory)

        market_report, news_report, sentiment_report, fundamentals_report = await asyncio.gather(
            market_task, news_task, sentiment_task, fundamentals_task
        )

        return {
            **state,
            "market_report": market_report,
            "news_report": news_report,
            "sentiment_report": sentiment_report,
            "fundamentals_report": fundamentals_report,
        }

    # --- Bull researcher node ---
    async def bull_researcher_node(state: dict) -> dict:
        debate = state.get("invest_debate", {})
        bear_args = debate.get("bear_arguments", [])
        counterpoints = bear_args[-1] if bear_args else ""

        thesis = await run_bull_researcher(
            llm, state["pair"],
            state["market_report"], state["news_report"],
            state["sentiment_report"], state["fundamentals_report"],
            bear_counterpoints=counterpoints,
            memory_context=state.get("similar_past_trades"),
        )

        debate = dict(state.get("invest_debate", {}))
        args = list(debate.get("bull_arguments", []))
        args.append(thesis)
        debate["bull_arguments"] = args

        return {**state, "bull_thesis": thesis, "invest_debate": debate}

    # --- Bear researcher node ---
    async def bear_researcher_node(state: dict) -> dict:
        debate = state.get("invest_debate", {})
        bull_args = debate.get("bull_arguments", [])
        counterpoints = bull_args[-1] if bull_args else ""

        thesis = await run_bear_researcher(
            llm, state["pair"],
            state["market_report"], state["news_report"],
            state["sentiment_report"], state["fundamentals_report"],
            bull_counterpoints=counterpoints,
            memory_context=state.get("similar_past_trades"),
        )

        debate = dict(state.get("invest_debate", {}))
        args = list(debate.get("bear_arguments", []))
        args.append(thesis)
        debate["bear_arguments"] = args
        debate["round_number"] = debate.get("round_number", 0) + 1

        return {**state, "bear_thesis": thesis, "invest_debate": debate}

    # --- Research manager node ---
    async def research_manager_node(state: dict) -> dict:
        debate = state.get("invest_debate", {})
        history = ""
        for i, (b, br) in enumerate(
            zip(debate.get("bull_arguments", []), debate.get("bear_arguments", []))
        ):
            history += f"\n--- Round {i+1} ---\nBull: {b}\nBear: {br}\n"

        verdict = await run_research_manager(
            deep_llm, state["pair"], state["bull_thesis"], state["bear_thesis"],
            debate_history=history,
            memory_context=state.get("similar_past_trades"),
        )
        return {**state, "research_verdict": verdict}

    # --- Trader node ---
    async def trader_node(state: dict) -> dict:
        proposal = await run_trader(
            llm, state["pair"], state["research_verdict"],
            config.get("current_positions", {}),
            config.get("account_balance", 10000),
            config.get("current_stage", "paper"),
            config.get("max_position_size_pct", 5.0),
            memory_context=state.get("similar_past_trades"),
        )
        return {**state, "trade_proposal": proposal}

    # --- Risk debate nodes ---
    async def aggressive_node(state: dict) -> dict:
        proposal_str = state["trade_proposal"].model_dump_json() if hasattr(state["trade_proposal"], "model_dump_json") else json.dumps(state["trade_proposal"])
        view = await run_aggressive_debator(llm, state["pair"], proposal_str)
        debate = dict(state.get("risk_debate", {}))
        debate["aggressive_view"] = view
        return {**state, "risk_debate": debate}

    async def conservative_node(state: dict) -> dict:
        proposal_str = state["trade_proposal"].model_dump_json() if hasattr(state["trade_proposal"], "model_dump_json") else json.dumps(state["trade_proposal"])
        view = await run_conservative_debator(llm, state["pair"], proposal_str)
        debate = dict(state.get("risk_debate", {}))
        debate["conservative_view"] = view
        return {**state, "risk_debate": debate}

    async def neutral_node(state: dict) -> dict:
        debate = state.get("risk_debate", {})
        proposal_str = state["trade_proposal"].model_dump_json() if hasattr(state["trade_proposal"], "model_dump_json") else json.dumps(state["trade_proposal"])
        view = await run_neutral_debator(
            llm, state["pair"], proposal_str,
            debate.get("aggressive_view", ""), debate.get("conservative_view", ""),
        )
        debate = dict(debate)
        debate["neutral_view"] = view
        debate["consensus"] = view
        debate["round_number"] = debate.get("round_number", 0) + 1
        return {**state, "risk_debate": debate}

    # --- Portfolio manager node ---
    async def portfolio_manager_node(state: dict) -> dict:
        proposal_str = state["trade_proposal"].model_dump_json() if hasattr(state["trade_proposal"], "model_dump_json") else json.dumps(state["trade_proposal"])
        consensus = state.get("risk_debate", {}).get("consensus", "")
        stage = config.get("current_stage", "paper")
        stage_rules = config.get("stages", {}).get(stage, {})

        decision = await run_portfolio_manager(
            deep_llm, state["pair"], proposal_str, consensus,
            config.get("portfolio_state", {}), stage, stage_rules,
            memory_context=state.get("similar_past_trades"),
        )
        return {**state, "final_decision": decision}

    # --- Add nodes ---
    graph.add_node("analysts", analyst_node)
    graph.add_node("bull_researcher", bull_researcher_node)
    graph.add_node("bear_researcher", bear_researcher_node)
    graph.add_node("research_manager", research_manager_node)
    graph.add_node("trader", trader_node)
    graph.add_node("aggressive_debator", aggressive_node)
    graph.add_node("conservative_debator", conservative_node)
    graph.add_node("neutral_debator", neutral_node)
    graph.add_node("portfolio_manager", portfolio_manager_node)

    # --- Add edges ---
    graph.set_entry_point("analysts")
    graph.add_edge("analysts", "bull_researcher")
    graph.add_edge("bull_researcher", "bear_researcher")

    # After bear researcher: continue debate or go to research manager
    graph.add_conditional_edges(
        "bear_researcher",
        should_continue_invest_debate,
        {"bull_researcher": "bull_researcher", "research_manager": "research_manager"},
    )

    graph.add_edge("research_manager", "trader")

    # After trader: execute or hold
    graph.add_conditional_edges(
        "trader",
        should_execute_trade,
        {"risk_debate": "aggressive_debator", "end": END},
    )

    graph.add_edge("aggressive_debator", "conservative_debator")
    graph.add_edge("conservative_debator", "neutral_debator")

    # After neutral: continue risk debate or go to portfolio manager
    graph.add_conditional_edges(
        "neutral_debator",
        should_continue_risk_debate,
        {"aggressive_debator": "aggressive_debator", "portfolio_manager": "portfolio_manager"},
    )

    # After portfolio manager: execute or end
    graph.add_conditional_edges(
        "portfolio_manager",
        should_execute_final,
        {"execute": END, "end": END},
    )

    return graph.compile()
