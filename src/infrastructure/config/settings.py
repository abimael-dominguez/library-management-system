from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    """Application-wide settings loaded from environment variables.

    Centralises every configurable value with sensible defaults so the
    application can run locally without any environment setup.
    """

    app_name: str = "Library Management System"
    app_env: str = os.getenv("APP_ENV", "local")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/local/library.db")
    auto_create_db: bool = os.getenv("AUTO_CREATE_DB", "true").lower() == "true"
    cors_origins: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000",
            ).split(",")
            if origin.strip()
        ]
    )


settings = Settings()
