from __future__ import annotations

from ...domain.entities.loan import Loan, LoanStatus
from ...domain.interfaces.loan_repository import LoanRepository


class GetLoanUseCase:
    """Retrieves a single loan by ID with computed status."""

    def __init__(self, loan_repo: LoanRepository) -> None:
        self._loan_repo = loan_repo

    def execute(self, *, loan_id: str) -> Loan | None:
        loan = self._loan_repo.get_loan_by_id(loan_id)
        if not loan:
            return None
        if loan.status == LoanStatus.IN_PROGRESS and loan.is_overdue:
            loan.status = LoanStatus.OVERDUE
        return loan
