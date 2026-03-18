from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...domain.entities.loan import Loan, LoanStatus
from ...domain.repositories.loan_repository import LoanRepository
from ..models import LoanModel


def to_domain_loan(model: LoanModel) -> Loan:
    return Loan(
        loan_id=model.loan_id,
        book_copy_id=model.book_copy_id,
        member_id=model.member_id,
        employee_id=model.employee_id,
        loan_date=model.loan_date,
        due_date=model.due_date,
        actual_return_date=model.actual_return_date,
        status=LoanStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyLoanRepository(LoanRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_loan(self, loan: Loan) -> Loan:
        self.db.add(
            LoanModel(
                loan_id=loan.loan_id,
                book_copy_id=loan.book_copy_id,
                member_id=loan.member_id,
                employee_id=loan.employee_id,
                loan_date=loan.loan_date,
                due_date=loan.due_date,
                actual_return_date=loan.actual_return_date,
                status=loan.status.value,
            )
        )
        return loan

    def get_loan_by_id(self, loan_id: str, for_update: bool = False) -> Loan | None:
        stmt = select(LoanModel).where(LoanModel.loan_id == loan_id)
        if for_update:
            stmt = stmt.with_for_update()
        model = self.db.scalars(stmt).first()
        return to_domain_loan(model) if model else None

    def list_loans(self, limit: int = 50) -> list[Loan]:
        stmt = select(LoanModel).order_by(LoanModel.created_at.desc()).limit(limit)
        return [to_domain_loan(model) for model in self.db.scalars(stmt).all()]

    def get_active_loans_by_book_copy_id(self, book_copy_id: str) -> list[Loan]:
        stmt = select(LoanModel).where(
            LoanModel.book_copy_id == book_copy_id,
            LoanModel.status == LoanStatus.IN_PROGRESS.value,
        )
        return [to_domain_loan(model) for model in self.db.scalars(stmt).all()]

    def get_overdue_loans(self, today: date | None = None) -> list[Loan]:
        today = today or date.today()
        stmt = select(LoanModel).where(
            LoanModel.status == LoanStatus.IN_PROGRESS.value,
            LoanModel.due_date < today,
        )
        return [to_domain_loan(model) for model in self.db.scalars(stmt).all()]
