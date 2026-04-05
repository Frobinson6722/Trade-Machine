"""Pydantic request/response schemas for all API endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# --- Trade schemas ---

class TradeResponse(BaseModel):
    id: int
    cycle_id: str
    pair: str
    side: str
    size_usd: float
    entry_price: float
    exit_price: float | None
    stop_loss: float | None
    take_profit: float | None
    status: str
    pnl: float | None
    pnl_pct: float | None
    stage: str
    mode: str
    exit_trigger: str | None
    opened_at: datetime
    closed_at: datetime | None


class TradeListResponse(BaseModel):
    trades: list[TradeResponse]
    total: int


# --- Agent log schemas ---

class AgentLogResponse(BaseModel):
    id: int
    cycle_id: str
    agent_name: str
    agent_type: str
    content: str
    created_at: datetime


class AgentLogListResponse(BaseModel):
    logs: list[AgentLogResponse]
    total: int


# --- Portfolio schemas ---

class PositionResponse(BaseModel):
    pair: str
    entry_price: float
    current_price: float
    quantity: float
    unrealized_pnl: float
    unrealized_pnl_pct: float


class PortfolioResponse(BaseModel):
    total_value: float
    cash_balance: float
    positions: list[PositionResponse]
    unrealized_pnl: float
    realized_pnl: float


class EquityCurvePoint(BaseModel):
    timestamp: datetime
    value: float


class EquityCurveResponse(BaseModel):
    points: list[EquityCurvePoint]


# --- Learning schemas ---

class ReflectionResponse(BaseModel):
    id: int
    pair: str
    reflection_text: str
    tags: list[str]
    trade_outcome: str
    created_at: datetime


class HypothesisResponse(BaseModel):
    id: int
    pair: str
    hypothesis: str
    status: str
    test_results: str | None
    rule_change: str | None
    created_at: datetime


class StrategyUpdateResponse(BaseModel):
    id: int
    description: str
    parameter_changes: dict[str, Any]
    old_values: dict[str, Any] | None
    created_at: datetime


class LearningResponse(BaseModel):
    reflections: list[ReflectionResponse]
    hypotheses: list[HypothesisResponse]
    strategy_updates: list[StrategyUpdateResponse]
    current_parameters: dict[str, Any]


# --- Session schemas ---

class SessionStartRequest(BaseModel):
    mode: str = "paper"
    config: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    id: int
    status: str
    mode: str
    stage: str
    started_at: datetime | None
    stopped_at: datetime | None


# --- Settings schemas ---

class SettingsResponse(BaseModel):
    llm_provider: str
    llm_model: str
    trading_pairs: list[str]
    cycle_interval_seconds: int
    max_position_size_pct: float
    max_portfolio_allocation_pct: float
    default_stop_loss_pct: float
    default_take_profit_pct: float
    current_stage: str
    mode: str


class SettingsUpdateRequest(BaseModel):
    llm_provider: str | None = None
    llm_model: str | None = None
    trading_pairs: list[str] | None = None
    cycle_interval_seconds: int | None = None
    max_position_size_pct: float | None = None
    max_portfolio_allocation_pct: float | None = None
    default_stop_loss_pct: float | None = None
    default_take_profit_pct: float | None = None


# --- Stats schemas ---

class StatsResponse(BaseModel):
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    avg_pnl: float
    total_reflections: int
    validated_hypotheses: int
    strategy_updates: int
    current_stage: str
    sharpe_ratio: float | None = None
    max_drawdown: float | None = None


# --- WebSocket schemas ---

class WSMessage(BaseModel):
    type: str  # trade_update, agent_activity, pnl_tick, status_change
    data: dict[str, Any]
