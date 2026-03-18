from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class BookCopyStatus(StrEnum):
    AVAILABLE = "available"
    LOANED = "loaned"
    DAMAGED = "damaged"
    LOST = "lost"


@dataclass
class Book:
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


@dataclass
class BookCopy:
    book_copy_id: str
    book_id: str
    status: BookCopyStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None
