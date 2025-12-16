from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.book import Book, BookCopy


class BookRepository(ABC):
    @abstractmethod
    async def create_book(self, book: Book) -> Book:
        pass

    @abstractmethod
    async def get_book_by_id(self, book_id: str) -> Optional[Book]:
        pass

    @abstractmethod
    async def search_books(self, query: str, limit: int = 10) -> List[Book]:
        pass

    @abstractmethod
    async def autocomplete_books(self, query: str, limit: int = 5) -> List[dict]:
        pass

    @abstractmethod
    async def list_books(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[Book], Optional[str]]:
        pass

    @abstractmethod
    async def update_book(self, book: Book) -> Book:
        pass

    @abstractmethod
    async def delete_book(self, book_id: str) -> bool:
        pass


class BookCopyRepository(ABC):
    @abstractmethod
    async def create_book_copy(self, book_copy: BookCopy) -> BookCopy:
        pass

    @abstractmethod
    async def get_book_copy_by_id(self, book_copy_id: str) -> Optional[BookCopy]:
        pass

    @abstractmethod
    async def get_copies_by_book_id(self, book_id: str) -> List[BookCopy]:
        pass

    @abstractmethod
    async def update_book_copy(self, book_copy: BookCopy) -> BookCopy:
        pass