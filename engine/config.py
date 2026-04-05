"""Default configuration for the Trade Machine engine."""

import os
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    # LLM settings — Claude only
    "llm_provider": "anthropic",
    "llm_model": os.getenv("LLM_MODEL", "claude-sonnet-4-20250514"),
    "deep_think_model": os.getenv("DEEP_THINK_MODEL", "claude-sonnet-4-20250514"),
    "quick_think_model": os.getenv("QUICK_THINK_MODEL", "claude-haiku-4-5-20251001"),
    "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),

    # Trading pairs
    "trading_pairs": os.getenv("DEFAULT_TRADING_PAIRS", "XRP-USD,DOGE-USD").split(","),

    # Cycle settings
    "cycle_interval_seconds": int(os.getenv("CYCLE_INTERVAL_SECONDS", "900")),
    "max_debate_rounds": 2,
    "max_risk_discuss_rounds": 2,
    "max_recur_limit": 50,

    # Risk parameters
    "max_position_size_pct": 5.0,
    "max_portfolio_allocation_pct": 25.0,
    "default_stop_loss_pct": 3.0,
    "default_take_profit_pct": 6.0,

    # Stage escalation thresholds
    "stages": {
        "paper": {
            "initial_balance": 10000.0,
            "min_trades_to_graduate": 100,
            "min_win_rate": 0.55,
        },
        "micro": {
            "trade_size_usd": 1.0,
            "min_trades_to_graduate": 1000,
            "min_win_rate": 0.52,
        },
        "graduated": {
            "sizes_usd": [2.0, 5.0, 10.0],
            "trades_per_level": 200,
            "min_win_rate": 0.52,
        },
    },

    # Robinhood
    "robinhood_username": os.getenv("ROBINHOOD_USERNAME", ""),
    "robinhood_password": os.getenv("ROBINHOOD_PASSWORD", ""),
    "robinhood_mfa_code": os.getenv("ROBINHOOD_MFA_CODE", ""),

    # Data providers
    "cryptopanic_api_key": os.getenv("CRYPTOPANIC_API_KEY", ""),

    # Nightly learner
    "nightly_learn_hour_utc": 0,

    # Output
    "output_language": "English",

    # Directories
    "data_dir": os.getenv("DATA_DIR", "./data"),
    "results_dir": os.getenv("RESULTS_DIR", "./results"),
}
