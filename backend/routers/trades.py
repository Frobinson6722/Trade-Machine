"""Trade history endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Trade
from backend.schemas import TradeResponse, TradeListResponse

router = APIRouter()


@router.get("", response_model=TradeListResponse)
async def list_trades(
    request: Request,
    pair: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List trades — from DB first, fallback to engine memory."""
    # Try DB first
    query = select(Trade).order_by(Trade.opened_at.desc())
    if pair:
        query = query.where(Trade.pair == pair)
    if status:
        query = query.where(Trade.status == status)

    count_query = select(func.count(Trade.id))
    if pair:
        count_query = count_query.where(Trade.pair == pair)
    if status:
        count_query = count_query.where(Trade.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    db_trades = result.scalars().all()

    if db_trades:
        return TradeListResponse(
            trades=[TradeResponse.model_validate(t.__dict__) for t in db_trades],
            total=total,
        )

    # Fallback: read from engine's in-memory journal
    bridge = request.app.state.engine_bridge
    if bridge.scheduler:
        journal_trades = bridge.scheduler.memory.journal.get_recent_trades(limit)
        if pair:
            journal_trades = [t for t in journal_trades if t.get("pair") == pair]
        if status:
            journal_trades = [t for t in journal_trades if t.get("status") == status]

        trades = []
        for i, t in enumerate(reversed(journal_trades)):
            trades.append(TradeResponse(
                id=i + 1,
                cycle_id=t.get("cycle_id", ""),
                pair=t.get("pair", ""),
                side=t.get("action", "BUY"),
                size_usd=t.get("size_usd", 0),
                entry_price=t.get("entry_price", 0),
                exit_price=t.get("exit_price"),
                stop_loss=t.get("stop_loss"),
                take_profit=t.get("take_profit"),
                status=t.get("status", "open"),
                pnl=t.get("pnl"),
                pnl_pct=t.get("pnl_pct"),
                stage=t.get("stage", "paper"),
                mode="paper",
                exit_trigger=t.get("exit_trigger"),
                opened_at=datetime.fromisoformat(t["opened_at"]) if t.get("opened_at") else datetime.now(),
                closed_at=datetime.fromisoformat(t["closed_at"]) if t.get("closed_at") else None,
            ))
        return TradeListResponse(trades=trades, total=len(trades))

    return TradeListResponse(trades=[], total=0)


@router.get("/{trade_id}")
async def get_trade(trade_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Get a specific trade by ID."""
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if trade:
        return TradeResponse.model_validate(trade.__dict__)

    # Fallback to journal
    bridge = request.app.state.engine_bridge
    if bridge.scheduler:
        entries = bridge.scheduler.memory.journal.entries
        if 0 < trade_id <= len(entries):
            t = entries[trade_id - 1]
            return {
                "id": trade_id,
                "cycle_id": t.get("cycle_id", ""),
                "pair": t.get("pair", ""),
                "side": t.get("action", ""),
                "entry_price": t.get("entry_price", 0),
                "pnl": t.get("pnl"),
                "reflection": t.get("reflection"),
                "agent_reasoning": t.get("agent_reasoning", {}),
            }

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Trade not found")
