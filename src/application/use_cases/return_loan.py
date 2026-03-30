from __future__ import annotations

from datetime import date

from ...domain.entities.book_copy_status import BookCopyStatus
from ...domain.entities.loan import Loan, LoanStatus
from ...domain.exceptions import DomainError
from ...domain.interfaces.book_copy_repository import BookCopyRepository
from ...domain.interfaces.loan_repository import LoanRepository
from ..dtos.loan_dto import LoanReturnRequest
from ..interfaces.unit_of_work import UnitOfWork


class ReturnLoanUseCase:
    """Processes a loan return, marking the book copy as available."""

    def __init__(
        self,
        loan_repo: LoanRepository,
        book_copy_repo: BookCopyRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._loan_repo = loan_repo
        self._book_copy_repo = book_copy_repo
        self._unit_of_work = unit_of_work

    def execute(self, *, loan_id: str, payload: LoanReturnRequest) -> Loan:
        loan = self._loan_repo.get_loan_by_id(loan_id, for_update=True)
        if not loan:
            raise DomainError("Loan not found.")
        if loan.status == LoanStatus.IN_PROGRESS and loan.is_overdue:
            loan.status = LoanStatus.OVERDUE
        if loan.status == LoanStatus.RETURNED:
            raise DomainError("Loan already returned.")

        book_copy = self._book_copy_repo.get_book_copy_by_id(loan.book_copy_id, for_update=True)
        if not book_copy:
            raise DomainError("Book copy not found.")

        return_date = payload.actual_return_date or date.today()
        if return_date < loan.loan_date:
            raise DomainError("Return date must be on or after the loan date.")

        loan.actual_return_date = return_date
        loan.status = LoanStatus.RETURNED
        book_copy.status = BookCopyStatus.AVAILABLE
        self._loan_repo.update_loan(loan)
        self._book_copy_repo.update_book_copy(book_copy)
        self._unit_of_work.commit()

        updated = self._loan_repo.get_loan_by_id(loan.loan_id)
        if updated and updated.status == LoanStatus.IN_PROGRESS and updated.is_overdue:
            updated.status = LoanStatus.OVERDUE
        return updated if updated else loan
