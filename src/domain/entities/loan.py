from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from enum import Enum


class LoanStatus(Enum):
    IN_PROGRESS = "Prestado"
    RETURNED = "Disponible"
    OVERDUE = "Vencido"


@dataclass
class Loan:
    loan_id: str
    book_copy_id: str
    member_id: str
    employee_id: Optional[str]
    loan_date: date
    due_date: date
    actual_return_date: Optional[date] = None
    status: LoanStatus = LoanStatus.IN_PROGRESS
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_overdue(self) -> bool:
        if self.status == LoanStatus.RETURNED:
            return False
        return date.today() > self.due_date