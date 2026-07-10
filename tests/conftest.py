from __future__ import annotations

from collections.abc import Generator
import os

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from src.infrastructure.persistence import models  # noqa: F401
from src.infrastructure.persistence.database import Base


@pytest.fixture
def db_session(tmp_path) -> Generator[Session, None, None]:
    configured_url = os.getenv("DATABASE_URL", "")
    database_url = configured_url if configured_url.startswith("postgresql") else f"sqlite:///{tmp_path / 'test.db'}"

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        database_url,
        future=True,
        connect_args=connect_args,
    )

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
