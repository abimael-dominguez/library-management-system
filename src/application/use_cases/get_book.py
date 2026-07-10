from __future__ import annotations

from ...domain.entities.book import Book
from ...domain.interfaces.book_copy_repository import BookCopyRepository
from ...domain.interfaces.book_repository import BookRepository


class GetBookUseCase:
    """Retrieves a single book by ID with availability info."""

    def __init__(
        self,
        book_repo: BookRepository,
        book_copy_repo: BookCopyRepository,
    ) -> None:
        self._book_repo = book_repo
        self._book_copy_repo = book_copy_repo

    def execute(self, *, book_id: str) -> Book | None:
        book = self._book_repo.get_book_by_id(book_id)
        if not book:
            return None
        book.total_copies = self._book_copy_repo.count_total_copies(book.book_id)
        book.available_copies = self._book_copy_repo.count_available_copies(book.book_id)
        book.first_available_copy_id = self._book_copy_repo.get_first_available_copy_id(book.book_id)
        return book
