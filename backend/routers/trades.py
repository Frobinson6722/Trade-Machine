"""Trade history endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Trade
from backend.schemas import TradeResponse, TradeListResponse

router = APIRouter()


@router.get("", response_model=TradeListResponse)
async def list_trades(
    pair: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List trades with optional filters."""
    query = select(Trade).order_by(Trade.opened_at.desc())

    if pair:
        query = query.where(Trade.pair == pair)
    if status:
        query = query.where(Trade.status == status)

    # Count total
    count_query = select(func.count(Trade.id))
    if pair:
        count_query = count_query.where(Trade.pair == pair)
    if status:
        count_query = count_query.where(Trade.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    trades = result.scalars().all()

    return TradeListResponse(
        trades=[TradeResponse.model_validate(t.__dict__) for t in trades],
        total=total,
    )


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific trade by ID."""
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if not trade:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Trade not found")
    return TradeResponse.model_validate(trade.__dict__)
