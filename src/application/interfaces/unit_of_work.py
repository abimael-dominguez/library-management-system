from __future__ import annotations

from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Abstracts transaction boundaries so use cases remain persistence-agnostic.

    Every use case that mutates state receives a UnitOfWork through its
    constructor and calls ``commit`` or ``rollback`` without knowing
    anything about the underlying storage engine.
    """

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError
