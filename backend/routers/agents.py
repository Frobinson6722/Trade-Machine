"""Agent reasoning log endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import AgentLog
from backend.schemas import AgentLogResponse, AgentLogListResponse

router = APIRouter()


@router.get("/logs", response_model=AgentLogListResponse)
async def list_agent_logs(
    cycle_id: str | None = None,
    agent_name: str | None = None,
    agent_type: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List agent reasoning logs with optional filters."""
    query = select(AgentLog).order_by(AgentLog.created_at.desc())

    if cycle_id:
        query = query.where(AgentLog.cycle_id == cycle_id)
    if agent_name:
        query = query.where(AgentLog.agent_name == agent_name)
    if agent_type:
        query = query.where(AgentLog.agent_type == agent_type)

    count_query = select(func.count(AgentLog.id))
    if cycle_id:
        count_query = count_query.where(AgentLog.cycle_id == cycle_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.offset(offset).limit(limit))
    logs = result.scalars().all()

    return AgentLogListResponse(
        logs=[AgentLogResponse.model_validate(l.__dict__) for l in logs],
        total=total,
    )
