from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class LoanCreateRequest(BaseModel):
    book_copy_id: str = Field(..., min_length=1)
    member_id: str = Field(..., min_length=1)
    employee_id: str | None = None
    loan_date: date
    due_date: date


class LoanReturnRequest(BaseModel):
    actual_return_date: date | None = None


class LoanResponse(BaseModel):
    loan_id: str
    book_copy_id: str
    member_id: str
    employee_id: str | None
    loan_date: date
    due_date: date
    actual_return_date: date | None
    status: str
    created_at: datetime | None
    updated_at: datetime | None
