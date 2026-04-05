"""FastAPI application — main entry point for the Trade Machine backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.routers import trades, portfolio, agents, learning, sessions, settings as settings_router, ws
from backend.services.engine_bridge import EngineBridge

# Global engine bridge instance
engine_bridge = EngineBridge()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB and optionally start engine."""
    await init_db()
    app.state.engine_bridge = engine_bridge
    yield
    # Shutdown: stop the engine if running
    if engine_bridge.scheduler:
        await engine_bridge.stop()


app = FastAPI(
    title="Trade Machine",
    description="Autonomous self-learning crypto trading bot API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(trades.router, prefix="/api/trades", tags=["Trades"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(learning.router, prefix="/api/learning", tags=["Learning"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])
app.include_router(ws.router, tags=["WebSocket"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    status = engine_bridge.get_status() if engine_bridge.scheduler else {"running": False}
    return {"status": "ok", "engine": status}
