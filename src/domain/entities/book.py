from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .book_copy import BookCopy
from .book_copy_status import BookCopyStatus

# Re-export for backward compatibility — importers can still do
# ``from domain.entities.book import Book, BookCopy, BookCopyStatus``
__all__ = ["Book", "BookCopy", "BookCopyStatus"]


@dataclass
class Book:
    """Represents a catalogued title in the library."""

    book_id: str
    title: str
    author: str
    isbn: str | None = None
    publisher: str | None = None
    publication_year: int | None = None
    genre: str | None = None
    pages: int | None = None
    max_loan_weeks: int = 3
    total_copies: int = 1
    available_copies: int = 0
    first_available_copy_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
