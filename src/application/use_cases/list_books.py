from __future__ import annotations

from ...domain.entities.book import Book
from ...domain.interfaces.book_copy_repository import BookCopyRepository
from ...domain.interfaces.book_repository import BookRepository


class ListBooksUseCase:
    """Retrieves a paginated list of books with availability info."""

    def __init__(
        self,
        book_repo: BookRepository,
        book_copy_repo: BookCopyRepository,
    ) -> None:
        self._book_repo = book_repo
        self._book_copy_repo = book_copy_repo

    def execute(self, *, limit: int = 50) -> list[Book]:
        books = self._book_repo.list_books(limit)
        return [self._enrich(book) for book in books]

    def _enrich(self, book: Book) -> Book:
        """Attach availability info that requires repository lookups."""
        book.total_copies = self._book_copy_repo.count_total_copies(book.book_id)
        book.available_copies = self._book_copy_repo.count_available_copies(book.book_id)
        book.first_available_copy_id = self._book_copy_repo.get_first_available_copy_id(book.book_id)
        return book
