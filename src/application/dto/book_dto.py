from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BookCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str | None = Field(default=None, max_length=17)
    publisher: str | None = Field(default=None, max_length=255)
    publication_year: int | None = Field(default=None, ge=1000, le=2100)
    genre: str | None = Field(default=None, max_length=100)
    pages: int | None = Field(default=None, ge=1)
    max_loan_weeks: int = Field(default=3, ge=1, le=52)
    total_copies: int = Field(default=1, ge=1, le=50)


class BookResponse(BaseModel):
    book_id: str
    title: str
    author: str
    isbn: str | None
    publisher: str | None
    publication_year: int | None
    genre: str | None
    pages: int | None
    max_loan_weeks: int
    total_copies: int
    available_copies: int
    first_available_copy_id: str | None
    created_at: datetime | None
    updated_at: datetime | None
