from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class LoanStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    RETURNED = "returned"
    OVERDUE = "overdue"


@dataclass
class Loan:
    loan_id: str
    book_copy_id: str
    member_id: str
    employee_id: str | None
    loan_date: date
    due_date: date
    actual_return_date: date | None = None
    status: LoanStatus = LoanStatus.IN_PROGRESS
    book_title: str | None = None
    book_author: str | None = None
    member_name: str | None = None
    employee_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def is_overdue(self) -> bool:
        return self.status == LoanStatus.IN_PROGRESS and self.due_date < date.today()
