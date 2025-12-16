from typing import List, Optional
import uuid
from datetime import datetime, date, timedelta

from domain.entities.loan import Loan, LoanStatus
from domain.entities.book import BookStatus
from domain.repositories.loan_repository import LoanRepository
from domain.repositories.book_repository import BookCopyRepository
from application.dto.loan_dto import CreateLoanRequest, LoanResponse, ReturnLoanRequest


class LoanService:
    def __init__(self, loan_repo: LoanRepository, book_copy_repo: BookCopyRepository):
        self.loan_repo = loan_repo
        self.book_copy_repo = book_copy_repo

    async def create_loan(self, request: CreateLoanRequest) -> LoanResponse:
        # Check if book copy is available
        book_copy = await self.book_copy_repo.get_book_copy_by_id(request.book_copy_id)
        if not book_copy or book_copy.status != BookStatus.AVAILABLE:
            raise ValueError("Book copy is not available for loan")

        # Check for active loans on this copy
        active_loans = await self.loan_repo.get_active_loans_by_book_copy_id(request.book_copy_id)
        if active_loans:
            raise ValueError("Book copy already has an active loan")

        loan_id = str(uuid.uuid4())
        now = datetime.utcnow()
        loan_date = request.loan_date
        due_date = request.due_date

        loan = Loan(
            loan_id=loan_id,
            book_copy_id=request.book_copy_id,
            member_id=request.member_id,
            employee_id=request.employee_id,
            loan_date=loan_date,
            due_date=due_date,
            status=LoanStatus.IN_PROGRESS,
            created_at=now,
            updated_at=now
        )

        created_loan = await self.loan_repo.create_loan(loan)

        # Update book copy status to Prestado
        book_copy.status = BookStatus.LOANED
        book_copy.updated_at = now
        await self.book_copy_repo.update_book_copy(book_copy)

        return LoanResponse(**created_loan.__dict__)

    async def return_loan(self, loan_id: str, request: ReturnLoanRequest) -> LoanResponse:
        loan = await self.loan_repo.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("Loan not found")

        if loan.status == LoanStatus.RETURNED:
            raise ValueError("Loan already returned")

        # Update loan
        loan.actual_return_date = request.actual_return_date or date.today()
        loan.status = LoanStatus.RETURNED
        loan.updated_at = datetime.utcnow()

        updated_loan = await self.loan_repo.update_loan(loan)

        # Update book copy status to Disponible
        book_copy = await self.book_copy_repo.get_book_copy_by_id(loan.book_copy_id)
        if book_copy:
            book_copy.status = BookStatus.AVAILABLE
            book_copy.updated_at = datetime.utcnow()
            await self.book_copy_repo.update_book_copy(book_copy)

        return LoanResponse(**updated_loan.__dict__)

    async def get_loan(self, loan_id: str) -> Optional[LoanResponse]:
        loan = await self.loan_repo.get_loan_by_id(loan_id)
        if not loan:
            return None
        return LoanResponse(**loan.__dict__)

    async def list_loans(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[LoanResponse], Optional[str]]:
        loans, next_key = await self.loan_repo.list_loans(limit, last_key)
        return [LoanResponse(**loan.__dict__) for loan in loans], next_key