from __future__ import annotations

from sqlalchemy.orm import Session

from ...application.interfaces.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Wraps a SQLAlchemy session to implement the application-layer UnitOfWork contract.

    Use cases call ``commit()`` / ``rollback()`` on this adapter without
    knowing that SQLAlchemy is the underlying persistence engine.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
