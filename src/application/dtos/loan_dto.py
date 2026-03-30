from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class LoanCreateRequest(BaseModel):
    """Input DTO for creating a new loan."""

    book_copy_id: str = Field(..., min_length=1)
    member_id: str = Field(..., min_length=1)
    employee_id: str | None = None
    loan_date: date
    due_date: date


class LoanReturnRequest(BaseModel):
    """Input DTO for returning a loaned book."""

    actual_return_date: date | None = None


class LoanResponse(BaseModel):
    """Output DTO returned when querying loan data."""

    loan_id: str
    book_copy_id: str
    member_id: str
    employee_id: str | None
    loan_date: date
    due_date: date
    actual_return_date: date | None
    status: str
    book_title: str | None = None
    book_author: str | None = None
    member_name: str | None = None
    employee_name: str | None = None
    created_at: datetime | None
    updated_at: datetime | None
