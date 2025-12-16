from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class CreateLoanRequest(BaseModel):
    book_copy_id: str = Field(..., min_length=1)
    member_id: str = Field(..., min_length=1)
    employee_id: Optional[str] = None
    loan_date: date = Field(..., description="Fecha de préstamo")
    due_date: date = Field(..., description="Fecha de vencimiento")


class ReturnLoanRequest(BaseModel):
    actual_return_date: Optional[date] = None


class LoanResponse(BaseModel):
    loan_id: str
    book_copy_id: str
    member_id: str
    employee_id: Optional[str]
    loan_date: date
    due_date: date
    actual_return_date: Optional[date]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]