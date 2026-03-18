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
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def is_overdue(self) -> bool:
        return self.status == LoanStatus.IN_PROGRESS and self.due_date < date.today()
