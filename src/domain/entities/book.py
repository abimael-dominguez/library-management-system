from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class BookStatus(Enum):
    AVAILABLE = "Disponible"
    LOANED = "Prestado"
    DAMAGED = "Dañado"
    LOST = "Perdido"


@dataclass
class Book:
    book_id: str
    title: str
    author: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    pages: Optional[int] = None
    max_loan_weeks: int = 3
    total_copies: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class BookCopy:
    book_copy_id: str
    book_id: str
    status: BookStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None