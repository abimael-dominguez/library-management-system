from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.book import Book
from .book_copy_repository import BookCopyRepository

# Re-export for backward compatibility
__all__ = ["BookRepository", "BookCopyRepository"]


class BookRepository(ABC):
    """Defines the contract for persisting and querying Book aggregates."""

    @abstractmethod
    def create_book(self, book: Book) -> Book:
        raise NotImplementedError

    @abstractmethod
    def get_book_by_id(self, book_id: str) -> Book | None:
        raise NotImplementedError

    @abstractmethod
    def search_books(self, query: str, limit: int = 10) -> list[Book]:
        raise NotImplementedError

    @abstractmethod
    def list_books(self, limit: int = 50, offset: int = 0) -> list[Book]:
        raise NotImplementedError

    @abstractmethod
    def count_books(self) -> int:
        raise NotImplementedError
