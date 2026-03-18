from __future__ import annotations

from datetime import date
from uuid import uuid4

from ...domain.entities.book import BookCopyStatus
from ...domain.entities.loan import Loan, LoanStatus
from ...domain.entities.member import MemberStatus
from ...domain.exceptions import DomainError
from ...domain.repositories.book_repository import BookCopyRepository
from ...domain.repositories.employee_repository import EmployeeRepository
from ...domain.repositories.loan_repository import LoanRepository
from ...domain.repositories.member_repository import MemberRepository
from ..dto.loan_dto import LoanCreateRequest, LoanReturnRequest


class LoanService:
    def __init__(
        self,
        loan_repo: LoanRepository,
        book_copy_repo: BookCopyRepository,
        member_repo: MemberRepository,
        employee_repo: EmployeeRepository,
        commit,
        rollback,
    ):
        self.loan_repo = loan_repo
        self.book_copy_repo = book_copy_repo
        self.member_repo = member_repo
        self.employee_repo = employee_repo
        self.commit = commit
        self.rollback = rollback

    def list_loans(self, limit: int = 50) -> list[Loan]:
        loans = self.loan_repo.list_loans(limit)
        return [self._normalize_status(loan) for loan in loans]

    def get_loan(self, loan_id: str) -> Loan | None:
        loan = self.loan_repo.get_loan_by_id(loan_id)
        return self._normalize_status(loan) if loan else None

    def create_loan(self, payload: LoanCreateRequest) -> Loan:
        if payload.due_date < payload.loan_date:
            raise DomainError("Due date must be on or after the loan date.")

        member = self.member_repo.get_member_by_id(payload.member_id)
        if not member:
            raise DomainError("Member not found.")
        if member.status != MemberStatus.ACTIVE:
            raise DomainError("Member is not active.")

        if payload.employee_id and not self.employee_repo.get_employee_by_id(payload.employee_id):
            raise DomainError("Employee not found.")

        book_copy = self.book_copy_repo.get_book_copy_by_id(payload.book_copy_id, for_update=True)
        if not book_copy:
            raise DomainError("Book copy not found.")
        if book_copy.status != BookCopyStatus.AVAILABLE:
            raise DomainError("Book copy is not available for loan.")
        if self.loan_repo.get_active_loans_by_book_copy_id(payload.book_copy_id):
            raise DomainError("Book copy already has an active loan.")

        loan = Loan(
            loan_id=str(uuid4()),
            book_copy_id=payload.book_copy_id,
            member_id=payload.member_id,
            employee_id=payload.employee_id,
            loan_date=payload.loan_date,
            due_date=payload.due_date,
            status=LoanStatus.IN_PROGRESS,
        )
        try:
            book_copy.status = BookCopyStatus.LOANED
            self.book_copy_repo.update_book_copy(book_copy)
            self.loan_repo.create_loan(loan)
            self.commit()
        except Exception as exc:
            self.rollback()
            raise DomainError("Loan could not be created.") from exc

        created = self.loan_repo.get_loan_by_id(loan.loan_id)
        if not created:
            raise DomainError("Loan was created but could not be reloaded.")
        return self._normalize_status(created)

    def return_loan(self, loan_id: str, payload: LoanReturnRequest) -> Loan:
        loan = self.loan_repo.get_loan_by_id(loan_id, for_update=True)
        if not loan:
            raise DomainError("Loan not found.")
        loan = self._normalize_status(loan)
        if loan.status == LoanStatus.RETURNED:
            raise DomainError("Loan already returned.")

        book_copy = self.book_copy_repo.get_book_copy_by_id(loan.book_copy_id, for_update=True)
        if not book_copy:
            raise DomainError("Book copy not found.")

        return_date = payload.actual_return_date or date.today()
        if return_date < loan.loan_date:
            raise DomainError("Return date must be on or after the loan date.")

        loan.actual_return_date = return_date
        loan.status = LoanStatus.RETURNED
        book_copy.status = BookCopyStatus.AVAILABLE
        self.book_copy_repo.update_book_copy(book_copy)
        self.commit()
        return loan

    def _normalize_status(self, loan: Loan) -> Loan:
        if loan.status == LoanStatus.IN_PROGRESS and loan.is_overdue:
            loan.status = LoanStatus.OVERDUE
        return loan
