#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.config.settings import settings
from src.infrastructure.persistence.database import Base
from src.infrastructure.persistence import models  # noqa: F401


SAFE_RESET_ENVS = {"local", "test"}


def ensure_safe_environment() -> None:
    if settings.app_env in SAFE_RESET_ENVS:
        return
    raise SystemExit("Refusing to reset database outside APP_ENV=local/test.")


def reset_postgres_schema(engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))


def reset_metadata_schema(engine) -> None:
    Base.metadata.drop_all(bind=engine)


def main() -> None:
    ensure_safe_environment()
    engine = create_engine(settings.database_url, future=True)
    try:
        if settings.database_url.startswith("postgresql"):
            reset_postgres_schema(engine)
        else:
            reset_metadata_schema(engine)
    finally:
        engine.dispose()
    print(f"Database schema reset for APP_ENV={settings.app_env}.")


if __name__ == "__main__":
    main()
