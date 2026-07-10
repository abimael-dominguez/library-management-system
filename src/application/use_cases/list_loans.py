from __future__ import annotations

from ...domain.entities.loan import Loan, LoanStatus
from ...domain.interfaces.loan_repository import LoanRepository


class ListLoansUseCase:
    """Retrieves a paginated list of loans with computed status."""

    def __init__(self, loan_repo: LoanRepository) -> None:
        self._loan_repo = loan_repo

    def execute(self, *, limit: int = 50, offset: int = 0, status: str = "all") -> list[Loan]:
        loans = self._loan_repo.list_loans(limit=limit, offset=offset, status=status)
        return [self._normalize_status(loan) for loan in loans]

    def count(self, *, status: str = "all") -> int:
        return self._loan_repo.count_loans(status=status)

    @staticmethod
    def _normalize_status(loan: Loan) -> Loan:
        """Promote an in-progress loan to OVERDUE when the due date has passed."""
        if loan.status == LoanStatus.IN_PROGRESS and loan.is_overdue:
            loan.status = LoanStatus.OVERDUE
        return loan
