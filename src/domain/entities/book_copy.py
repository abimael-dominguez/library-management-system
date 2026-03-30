from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .book_copy_status import BookCopyStatus


@dataclass
class BookCopy:
    """Represents a single physical copy of a book in the library."""

    book_copy_id: str
    book_id: str
    status: BookCopyStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None
