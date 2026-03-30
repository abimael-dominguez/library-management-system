from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...domain.entities.loan import Loan, LoanStatus
from ...domain.interfaces.loan_repository import LoanRepository
from ..persistence.models import BookCopyModel, BookModel, EmployeeModel, LoanModel, MemberModel


def _to_domain_loan(model: LoanModel) -> Loan:
    """Map a LoanModel ORM instance to the domain Loan entity.

    Eagerly populates denormalised display fields (book title, member name,
    etc.) from the joined relationships so that the application layer does
    not need to perform additional queries.
    """
    return Loan(
        loan_id=model.loan_id,
        book_copy_id=model.book_copy_id,
        member_id=model.member_id,
        employee_id=model.employee_id,
        loan_date=model.loan_date,
        due_date=model.due_date,
        actual_return_date=model.actual_return_date,
        status=LoanStatus(model.status),
        book_title=model.book_copy.book.title if model.book_copy and model.book_copy.book else None,
        book_author=model.book_copy.book.author if model.book_copy and model.book_copy.book else None,
        member_name=(
            f"{model.member.first_name} {model.member.last_name}".strip()
            if model.member
            else None
        ),
        employee_name=(
            f"{model.employee.first_name} {model.employee.last_name}".strip()
            if model.employee
            else None
        ),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyLoanRepository(LoanRepository):
    """SQLAlchemy-backed implementation of the LoanRepository interface."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_loan(self, loan: Loan) -> Loan:
        self._db.add(
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
        stmt = (
            select(LoanModel)
            .join(BookCopyModel, LoanModel.book_copy_id == BookCopyModel.book_copy_id)
            .join(BookModel, BookCopyModel.book_id == BookModel.book_id)
            .join(MemberModel, LoanModel.member_id == MemberModel.member_id)
            .outerjoin(EmployeeModel, LoanModel.employee_id == EmployeeModel.employee_id)
            .where(LoanModel.loan_id == loan_id)
        )
        if for_update:
            stmt = stmt.with_for_update()
        model = self._db.scalars(stmt).first()
        return _to_domain_loan(model) if model else None

    def update_loan(self, loan: Loan) -> Loan:
        model = self._db.get(LoanModel, loan.loan_id)
        if not model:
            return loan

        model.actual_return_date = loan.actual_return_date
        model.status = loan.status.value
        return loan

    def list_loans(self, limit: int = 50) -> list[Loan]:
        stmt = (
            select(LoanModel)
            .join(BookCopyModel, LoanModel.book_copy_id == BookCopyModel.book_copy_id)
            .join(BookModel, BookCopyModel.book_id == BookModel.book_id)
            .join(MemberModel, LoanModel.member_id == MemberModel.member_id)
            .outerjoin(EmployeeModel, LoanModel.employee_id == EmployeeModel.employee_id)
            .order_by(LoanModel.created_at.desc())
            .limit(limit)
        )
        return [_to_domain_loan(model) for model in self._db.scalars(stmt).all()]

    def get_active_loans_by_book_copy_id(self, book_copy_id: str) -> list[Loan]:
        stmt = select(LoanModel).where(
            LoanModel.book_copy_id == book_copy_id,
            LoanModel.status == LoanStatus.IN_PROGRESS.value,
        )
        return [_to_domain_loan(model) for model in self._db.scalars(stmt).all()]

    def get_overdue_loans(self, today: date | None = None) -> list[Loan]:
        today = today or date.today()
        stmt = select(LoanModel).where(
            LoanModel.status == LoanStatus.IN_PROGRESS.value,
            LoanModel.due_date < today,
        )
        return [_to_domain_loan(model) for model in self._db.scalars(stmt).all()]
