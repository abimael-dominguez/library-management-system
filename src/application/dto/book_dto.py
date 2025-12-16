from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateBookRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=17)
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=2100)
    genre: Optional[str] = Field(None, max_length=100)
    pages: Optional[int] = Field(None, ge=1)
    max_loan_weeks: int = Field(3, ge=1, le=52)
    total_copies: int = Field(1, ge=1)


class BookResponse(BaseModel):
    book_id: str
    title: str
    author: str
    isbn: Optional[str]
    publisher: Optional[str]
    publication_year: Optional[int]
    genre: Optional[str]
    pages: Optional[int]
    max_loan_weeks: int
    total_copies: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class SearchBooksRequest(BaseModel):
    q: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=50)


class AutocompleteRequest(BaseModel):
    q: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(book|member)$")
    limit: int = Field(5, ge=1, le=20)