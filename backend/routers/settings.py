"""Settings endpoints for configuration management."""

from fastapi import APIRouter, Depends, Request

from backend.auth import verify_token
from backend.schemas import SettingsResponse, SettingsUpdateRequest

router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings(request: Request):
    """Get current engine settings."""
    bridge = request.app.state.engine_bridge

    if bridge.scheduler:
        config = bridge.scheduler.config
        return SettingsResponse(
            llm_provider=config.get("llm_provider", "openai"),
            llm_model=config.get("llm_model", "gpt-4o"),
            trading_pairs=config.get("trading_pairs", ["BTC-USD"]),
            cycle_interval_seconds=config.get("cycle_interval_seconds", 900),
            max_position_size_pct=config.get("max_position_size_pct", 5.0),
            max_portfolio_allocation_pct=config.get("max_portfolio_allocation_pct", 25.0),
            default_stop_loss_pct=config.get("default_stop_loss_pct", 3.0),
            default_take_profit_pct=config.get("default_take_profit_pct", 6.0),
            current_stage=bridge.scheduler.stage_manager.get_current_stage(),
            mode=bridge.scheduler.executor.mode,
        )

    from engine.config import DEFAULT_CONFIG
    return SettingsResponse(
        llm_provider=DEFAULT_CONFIG["llm_provider"],
        llm_model=DEFAULT_CONFIG["llm_model"],
        trading_pairs=DEFAULT_CONFIG["trading_pairs"],
        cycle_interval_seconds=DEFAULT_CONFIG["cycle_interval_seconds"],
        max_position_size_pct=DEFAULT_CONFIG["max_position_size_pct"],
        max_portfolio_allocation_pct=DEFAULT_CONFIG["max_portfolio_allocation_pct"],
        default_stop_loss_pct=DEFAULT_CONFIG["default_stop_loss_pct"],
        default_take_profit_pct=DEFAULT_CONFIG["default_take_profit_pct"],
        current_stage="paper",
        mode="paper",
    )


@router.put("")
async def update_settings(
    updates: SettingsUpdateRequest,
    request: Request,
    _token: str = Depends(verify_token),
):
    """Update engine settings. Takes effect on next cycle."""
    bridge = request.app.state.engine_bridge

    if bridge.scheduler:
        update_dict = updates.model_dump(exclude_none=True)
        bridge.scheduler.config.update(update_dict)
        return {"status": "updated", "changes": update_dict}

    return {"status": "no_session", "message": "Settings will apply when a session starts"}
