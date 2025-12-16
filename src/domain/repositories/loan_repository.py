from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.loan import Loan


class LoanRepository(ABC):
    @abstractmethod
    async def create_loan(self, loan: Loan) -> Loan:
        pass

    @abstractmethod
    async def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        pass

    @abstractmethod
    async def list_loans(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[Loan], Optional[str]]:
        pass

    @abstractmethod
    async def get_loans_by_member_id(self, member_id: str) -> List[Loan]:
        pass

    @abstractmethod
    async def get_active_loans_by_book_copy_id(self, book_copy_id: str) -> List[Loan]:
        pass

    @abstractmethod
    async def update_loan(self, loan: Loan) -> Loan:
        pass

    @abstractmethod
    async def get_overdue_loans(self) -> List[Loan]:
        pass