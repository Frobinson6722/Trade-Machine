"""Trading session lifecycle endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import TradingSession
from backend.schemas import SessionStartRequest, SessionResponse

router = APIRouter()


@router.post("/start", response_model=SessionResponse)
async def start_session(
    req: SessionStartRequest,
    request: Request,

    db: AsyncSession = Depends(get_db),
):
    """Start a new trading session."""
    bridge = request.app.state.engine_bridge

    if bridge.scheduler and bridge.scheduler.running:
        raise HTTPException(status_code=409, detail="A session is already running")

    # Create DB record
    session = TradingSession(
        status="running",
        mode=req.mode,
        stage="paper",
        config_snapshot=req.config,
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Start engine
    await bridge.start(config=req.config)

    if req.mode == "live":
        bridge.scheduler.executor.set_mode("live")

    return SessionResponse(
        id=session.id,
        status=session.status,
        mode=session.mode,
        stage=session.stage,
        started_at=session.started_at,
        stopped_at=session.stopped_at,
    )


@router.post("/stop")
async def stop_session(
    request: Request,

):
    """Stop the running trading session."""
    bridge = request.app.state.engine_bridge
    if not bridge.scheduler or not bridge.scheduler.running:
        raise HTTPException(status_code=409, detail="No session is running")

    await bridge.stop()
    return {"status": "stopped"}


@router.post("/pause")
async def pause_session(
    request: Request,

):
    """Pause the running trading session."""
    bridge = request.app.state.engine_bridge
    if not bridge.scheduler or not bridge.scheduler.running:
        raise HTTPException(status_code=409, detail="No session is running")

    await bridge.scheduler.pause()
    return {"status": "paused"}


@router.post("/resume")
async def resume_session(
    request: Request,

):
    """Resume a paused trading session."""
    bridge = request.app.state.engine_bridge
    if not bridge.scheduler:
        raise HTTPException(status_code=409, detail="No session exists")

    await bridge.scheduler.resume()
    return {"status": "running"}


@router.get("/status")
async def get_session_status(request: Request):
    """Get current session status."""
    bridge = request.app.state.engine_bridge
    return bridge.get_status()
