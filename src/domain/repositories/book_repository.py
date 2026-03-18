from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.book import Book, BookCopy


class BookRepository(ABC):
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
    def list_books(self, limit: int = 50) -> list[Book]:
        raise NotImplementedError


class BookCopyRepository(ABC):
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
