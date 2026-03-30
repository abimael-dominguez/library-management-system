from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.book_copy import BookCopy


class BookCopyRepository(ABC):
    """Defines the contract for persisting and querying BookCopy entities."""

    @abstractmethod
    def create_book_copy(self, book_copy: BookCopy) -> BookCopy:
        raise NotImplementedError

    @abstractmethod
    def get_book_copy_by_id(self, book_copy_id: str, for_update: bool = False) -> BookCopy | None:
        raise NotImplementedError

    @abstractmethod
    def update_book_copy(self, book_copy: BookCopy) -> BookCopy:
        raise NotImplementedError

    @abstractmethod
    def count_available_copies(self, book_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_first_available_copy_id(self, book_id: str) -> str | None:
        raise NotImplementedError
