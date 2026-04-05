"""Learning system endpoints — reflections, hypotheses, strategy updates."""

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import ReflectionEntry, StrategyUpdate
from backend.schemas import LearningResponse, ReflectionResponse, StrategyUpdateResponse

router = APIRouter()


@router.get("", response_model=LearningResponse)
async def get_learning_data(request: Request):
    """Get all learning-related data: reflections, hypotheses, strategy updates."""
    bridge = request.app.state.engine_bridge

    if bridge.scheduler:
        data = bridge.scheduler.memory.get_learning_data()
        return LearningResponse(
            reflections=[
                ReflectionResponse(
                    id=r.get("id", 0),
                    pair=r.get("pair", ""),
                    reflection_text=r.get("reflection", ""),
                    tags=r.get("tags", []),
                    trade_outcome=r.get("trade_outcome", ""),
                    created_at=r.get("created_at", "2024-01-01T00:00:00Z"),
                )
                for r in data.get("reflections", [])
            ],
            hypotheses=[],
            strategy_updates=[
                StrategyUpdateResponse(
                    id=u.get("id", 0),
                    description=u.get("description", ""),
                    parameter_changes=u.get("parameter_changes", {}),
                    old_values=u.get("old_values"),
                    created_at=u.get("created_at", "2024-01-01T00:00:00Z"),
                )
                for u in data.get("strategy_updates", [])
            ],
            current_parameters=data.get("current_parameters", {}),
        )

    return LearningResponse(
        reflections=[], hypotheses=[], strategy_updates=[], current_parameters={}
    )


@router.get("/reflections")
async def list_reflections(
    pair: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List reflections from the database."""
    query = select(ReflectionEntry).order_by(ReflectionEntry.created_at.desc())
    if pair:
        query = query.where(ReflectionEntry.pair == pair)
    query = query.limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/strategy-updates")
async def list_strategy_updates(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List strategy updates from the database."""
    result = await db.execute(
        select(StrategyUpdate).order_by(StrategyUpdate.created_at.desc()).limit(limit)
    )
    return result.scalars().all()
