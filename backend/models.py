"""SQLAlchemy ORM models for trade data persistence."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cycle_id = Column(String(20), unique=True, index=True)
    pair = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # BUY, SELL
    size_usd = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    status = Column(String(20), default="open")  # open, closed, cancelled
    pnl = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    stage = Column(String(20), nullable=False)
    mode = Column(String(10), default="paper")  # paper, live
    exit_trigger = Column(String(20), nullable=True)  # stop_loss, take_profit, manual
    opened_at = Column(DateTime, default=utcnow)
    closed_at = Column(DateTime, nullable=True)
    session_id = Column(Integer, ForeignKey("trading_sessions.id"), nullable=True)

    agent_logs = relationship("AgentLog", back_populates="trade", lazy="selectin")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    cycle_id = Column(String(20), index=True)
    agent_name = Column(String(50), nullable=False)
    agent_type = Column(String(30), nullable=False)  # analyst, researcher, debator, manager, trader
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    trade = relationship("Trade", back_populates="agent_logs")


class ReflectionEntry(Base):
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(Integer, nullable=True)
    cycle_id = Column(String(20), nullable=True)
    pair = Column(String(20), nullable=False)
    agent_name = Column(String(50), default="system")
    reflection_text = Column(Text, nullable=False)
    lesson_learned = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    trade_outcome = Column(String(10))  # win, loss
    created_at = Column(DateTime, default=utcnow)


class StrategyUpdate(Base):
    __tablename__ = "strategy_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger_trade_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    parameter_changes = Column(JSON, nullable=False)
    old_values = Column(JSON, nullable=True)
    performance_before = Column(JSON, nullable=True)
    performance_after = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    total_value = Column(Float, nullable=False)
    cash_balance = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0)
    realized_pnl_cumulative = Column(Float, default=0)


class TradingSession(Base):
    __tablename__ = "trading_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), default="stopped")  # running, paused, stopped
    mode = Column(String(10), default="paper")  # paper, live
    stage = Column(String(20), default="paper")
    config_snapshot = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
