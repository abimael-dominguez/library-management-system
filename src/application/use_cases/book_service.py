from __future__ import annotations

from uuid import uuid4

from ...domain.entities.book import Book, BookCopy, BookCopyStatus
from ...domain.exceptions import DomainError
from ...domain.repositories.book_repository import BookCopyRepository, BookRepository
from ..dto.book_dto import BookCreateRequest


class BookService:
    def __init__(self, book_repo: BookRepository, book_copy_repo: BookCopyRepository, commit, rollback):
        self.book_repo = book_repo
        self.book_copy_repo = book_copy_repo
        self.commit = commit
        self.rollback = rollback

    def list_books(self, limit: int = 50) -> list[Book]:
        books = self.book_repo.list_books(limit)
        return [self._enrich(book) for book in books]

    def get_book(self, book_id: str) -> Book | None:
        book = self.book_repo.get_book_by_id(book_id)
        return self._enrich(book) if book else None

    def search_books(self, query: str, limit: int = 10) -> list[Book]:
        books = self.book_repo.search_books(query, limit)
        return [self._enrich(book) for book in books]

    def create_book(self, payload: BookCreateRequest) -> Book:
        book_id = str(uuid4())
        book = Book(
            book_id=book_id,
            title=payload.title,
            author=payload.author,
            isbn=payload.isbn,
            publisher=payload.publisher,
            publication_year=payload.publication_year,
            genre=payload.genre,
            pages=payload.pages,
            max_loan_weeks=payload.max_loan_weeks,
            total_copies=payload.total_copies,
        )
        try:
            self.book_repo.create_book(book)
            for number in range(1, payload.total_copies + 1):
                self.book_copy_repo.create_book_copy(
                    BookCopy(
                        book_copy_id=f"{book_id}-{number:03d}",
                        book_id=book_id,
                        status=BookCopyStatus.AVAILABLE,
                    )
                )
            self.commit()
        except Exception as exc:
            self.rollback()
            raise DomainError("Book could not be saved. ISBN may already exist.") from exc

        created = self.book_repo.get_book_by_id(book_id)
        if not created:
            raise DomainError("Book was created but could not be reloaded.")
        return self._enrich(created)

    def _enrich(self, book: Book) -> Book:
        book.available_copies = self.book_copy_repo.count_available_copies(book.book_id)
        book.first_available_copy_id = self.book_copy_repo.get_first_available_copy_id(book.book_id)
        return book
