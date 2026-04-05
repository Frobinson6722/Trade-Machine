"""API usage and cost tracking endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_usage():
    """Get API usage summary with costs."""
    from engine.llm_clients.anthropic_client import usage_tracker
    return usage_tracker.get_summary()
