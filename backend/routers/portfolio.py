"""Portfolio and equity curve endpoints."""

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import PortfolioSnapshot
from backend.schemas import PortfolioResponse, PositionResponse, EquityCurveResponse, EquityCurvePoint

router = APIRouter()


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(request: Request):
    """Get current portfolio with live unrealized P&L for open positions."""
    bridge = request.app.state.engine_bridge

    if not bridge.scheduler:
        return PortfolioResponse(
            total_value=10000, cash_balance=10000, positions=[],
            unrealized_pnl=0, realized_pnl=0,
        )

    scheduler = bridge.scheduler
    paper = scheduler.executor.paper_trader
    positions_raw = paper.get_positions()
    stats = paper.get_stats()

    # Fetch current prices for open positions
    positions = []
    total_unrealized = 0.0
    for pair, pos in positions_raw.items():
        try:
            ticker = await scheduler.data_provider.get_ticker(pair)
            current_price = ticker.get("price", pos["entry_price"])
        except Exception:
            current_price = pos["entry_price"]

        entry = pos["entry_price"]
        qty = pos["quantity"]
        unrealized = (current_price - entry) * qty
        unrealized_pct = ((current_price / entry) - 1) * 100 if entry else 0
        total_unrealized += unrealized

        positions.append(PositionResponse(
            pair=pair,
            entry_price=entry,
            current_price=current_price,
            quantity=qty,
            unrealized_pnl=round(unrealized, 2),
            unrealized_pnl_pct=round(unrealized_pct, 2),
        ))

    realized = stats.get("total_pnl", 0)
    cash = paper.cash_balance

    return PortfolioResponse(
        total_value=round(cash + sum(p.quantity * p.current_price for p in positions), 2),
        cash_balance=round(cash, 2),
        positions=positions,
        unrealized_pnl=round(total_unrealized, 2),
        realized_pnl=round(realized, 2),
    )


@router.get("/equity-curve", response_model=EquityCurveResponse)
async def get_equity_curve(
    limit: int = Query(500, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """Get equity curve data points."""
    result = await db.execute(
        select(PortfolioSnapshot)
        .order_by(PortfolioSnapshot.timestamp.desc())
        .limit(limit)
    )
    snapshots = result.scalars().all()

    points = [
        EquityCurvePoint(timestamp=s.timestamp, value=s.total_value)
        for s in reversed(snapshots)
    ]
    return EquityCurveResponse(points=points)
