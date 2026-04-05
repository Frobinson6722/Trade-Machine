"""Backend configuration."""

import os
from typing import Any


class Settings:
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./trade_machine.db")

    # Auth
    AUTH_TOKEN: str = os.getenv("AUTH_TOKEN", "dev-token-change-me")

    # CORS
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # Engine config passthrough
    ENGINE_CONFIG: dict[str, Any] = {}


settings = Settings()
