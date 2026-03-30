from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ...domain.entities.book import Book
from ...domain.entities.book_copy import BookCopy
from ...domain.entities.book_copy_status import BookCopyStatus
from ...domain.interfaces.book_copy_repository import BookCopyRepository
from ...domain.interfaces.book_repository import BookRepository
from ..persistence.models import BookCopyModel, BookModel


def _to_domain_book(model: BookModel) -> Book:
    """Map a BookModel ORM instance to the domain Book entity."""
    return Book(
        book_id=model.book_id,
        title=model.title,
        author=model.author,
        isbn=model.isbn,
        publisher=model.publisher,
        publication_year=model.publication_year,
        genre=model.genre,
        pages=model.pages,
        max_loan_weeks=model.max_loan_weeks,
        total_copies=model.total_copies,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_domain_book_copy(model: BookCopyModel) -> BookCopy:
    """Map a BookCopyModel ORM instance to the domain BookCopy entity."""
    return BookCopy(
        book_copy_id=model.book_copy_id,
        book_id=model.book_id,
        status=BookCopyStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyBookRepository(BookRepository):
    """SQLAlchemy-backed implementation of the BookRepository interface."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_book(self, book: Book) -> Book:
        self._db.add(
            BookModel(
                book_id=book.book_id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                publisher=book.publisher,
                publication_year=book.publication_year,
                genre=book.genre,
                pages=book.pages,
                max_loan_weeks=book.max_loan_weeks,
                total_copies=book.total_copies,
            )
        )
        return book

    def get_book_by_id(self, book_id: str) -> Book | None:
        model = self._db.get(BookModel, book_id)
        return _to_domain_book(model) if model else None

    def search_books(self, query: str, limit: int = 10) -> list[Book]:
        term = f"%{query.lower()}%"
        stmt = (
            select(BookModel)
            .where(
                or_(
                    func.lower(BookModel.title).like(term),
                    func.lower(BookModel.author).like(term),
                    func.lower(func.coalesce(BookModel.isbn, "")).like(term),
                )
            )
            .order_by(BookModel.title)
            .limit(limit)
        )
        return [_to_domain_book(model) for model in self._db.scalars(stmt).all()]

    def list_books(self, limit: int = 50) -> list[Book]:
        stmt = select(BookModel).order_by(BookModel.title).limit(limit)
        return [_to_domain_book(model) for model in self._db.scalars(stmt).all()]


class SqlAlchemyBookCopyRepository(BookCopyRepository):
    """SQLAlchemy-backed implementation of the BookCopyRepository interface."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_book_copy(self, book_copy: BookCopy) -> BookCopy:
        self._db.add(
            BookCopyModel(
                book_copy_id=book_copy.book_copy_id,
                book_id=book_copy.book_id,
                status=book_copy.status.value,
            )
        )
        return book_copy

    def get_book_copy_by_id(self, book_copy_id: str, for_update: bool = False) -> BookCopy | None:
        stmt = select(BookCopyModel).where(BookCopyModel.book_copy_id == book_copy_id)
        if for_update:
            stmt = stmt.with_for_update()
        model = self._db.scalars(stmt).first()
        return _to_domain_book_copy(model) if model else None

    def update_book_copy(self, book_copy: BookCopy) -> BookCopy:
        model = self._db.get(BookCopyModel, book_copy.book_copy_id)
        if not model:
            raise ValueError("Book copy not found.")
        model.status = book_copy.status.value
        return book_copy

    def count_available_copies(self, book_id: str) -> int:
        stmt = select(func.count(BookCopyModel.book_copy_id)).where(
            BookCopyModel.book_id == book_id,
            BookCopyModel.status == BookCopyStatus.AVAILABLE.value,
        )
        return int(self._db.scalar(stmt) or 0)

    def get_first_available_copy_id(self, book_id: str) -> str | None:
        stmt = (
            select(BookCopyModel.book_copy_id)
            .where(
                BookCopyModel.book_id == book_id,
                BookCopyModel.status == BookCopyStatus.AVAILABLE.value,
            )
            .order_by(BookCopyModel.book_copy_id)
            .limit(1)
        )
        return self._db.scalar(stmt)
