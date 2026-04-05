"""State schemas for the LangGraph trading pipeline."""

from __future__ import annotations

from typing import Annotated, Any, Literal
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class TradeSignal(BaseModel):
    """Structured output from the trader agent."""
    action: Literal["BUY", "SELL", "HOLD"]
    pair: str
    size_pct: float = Field(ge=0, le=100, description="Position size as % of portfolio")
    entry_type: Literal["market", "limit"] = "market"
    limit_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    reasoning: str = ""


class FinalDecision(BaseModel):
    """Output from the portfolio manager."""
    approved: bool
    action: Literal["BUY", "SELL", "HOLD"]
    pair: str
    size_pct: float
    stop_loss: float | None = None
    take_profit: float | None = None
    modifications: str = ""
    reasoning: str = ""


class InvestDebateState(BaseModel):
    """Tracks the bull vs bear research debate."""
    round_number: int = 0
    max_rounds: int = 2
    bull_arguments: list[str] = Field(default_factory=list)
    bear_arguments: list[str] = Field(default_factory=list)
    verdict: str = ""


class RiskDebateState(BaseModel):
    """Tracks the risk management debate."""
    round_number: int = 0
    max_rounds: int = 2
    aggressive_view: str = ""
    conservative_view: str = ""
    neutral_view: str = ""
    consensus: str = ""


class TradingCycleState(BaseModel):
    """Full state for a single trading cycle through the LangGraph pipeline."""
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    pair: str = ""
    timestamp: str = ""

    # Raw data
    market_data: dict[str, Any] = Field(default_factory=dict)
    news_data: list[dict] = Field(default_factory=list)
    sentiment_data: dict[str, Any] = Field(default_factory=dict)
    onchain_data: dict[str, Any] = Field(default_factory=dict)

    # Analyst reports
    market_report: str = ""
    news_report: str = ""
    sentiment_report: str = ""
    fundamentals_report: str = ""

    # Research
    bull_thesis: str = ""
    bear_thesis: str = ""
    invest_debate: InvestDebateState = Field(default_factory=InvestDebateState)
    research_verdict: str = ""

    # Trade proposal
    trade_proposal: TradeSignal | None = None

    # Risk debate
    risk_debate: RiskDebateState = Field(default_factory=RiskDebateState)

    # Final decision
    final_decision: FinalDecision | None = None

    # Memory context
    similar_past_trades: list[str] = Field(default_factory=list)
    active_reflections: list[str] = Field(default_factory=list)
