from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from ..entities.loan import Loan


class LoanRepository(ABC):
    @abstractmethod
    def create_loan(self, loan: Loan) -> Loan:
        raise NotImplementedError

    @abstractmethod
    def get_loan_by_id(self, loan_id: str, for_update: bool = False) -> Loan | None:
        raise NotImplementedError

    @abstractmethod
    def list_loans(self, limit: int = 50) -> list[Loan]:
        raise NotImplementedError

    @abstractmethod
    def get_active_loans_by_book_copy_id(self, book_copy_id: str) -> list[Loan]:
        raise NotImplementedError

    @abstractmethod
    def get_overdue_loans(self, today: date | None = None) -> list[Loan]:
        raise NotImplementedError
