"""Portfolio and equity curve endpoints."""

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import PortfolioSnapshot
from backend.schemas import PortfolioResponse, EquityCurveResponse, EquityCurvePoint

router = APIRouter()


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(request: Request):
    """Get current portfolio status including positions and P&L."""
    bridge = request.app.state.engine_bridge

    if not bridge.scheduler:
        return PortfolioResponse(
            total_value=0, cash_balance=0, positions=[],
            unrealized_pnl=0, realized_pnl=0,
        )

    status = bridge.get_status()
    stats = status.get("stats", {})

    return PortfolioResponse(
        total_value=stats.get("total_pnl", 0) + 10000,
        cash_balance=10000,  # Will be replaced with real balance
        positions=[],
        unrealized_pnl=0,
        realized_pnl=stats.get("total_pnl", 0),
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
