from datetime import date, timedelta

import pytest

from src.application.dto.book_dto import BookCreateRequest
from src.application.dto.employee_dto import EmployeeCreateRequest
from src.application.dto.loan_dto import LoanCreateRequest, LoanReturnRequest
from src.application.dto.member_dto import MemberCreateRequest
from src.application.use_cases.book_service import BookService
from src.application.use_cases.employee_service import EmployeeService
from src.application.use_cases.loan_service import LoanService
from src.application.use_cases.member_service import MemberService
from src.domain.exceptions import DomainError
from src.infrastructure.repositories.book_repository import SqlAlchemyBookCopyRepository, SqlAlchemyBookRepository
from src.infrastructure.repositories.employee_repository import SqlAlchemyEmployeeRepository
from src.infrastructure.repositories.loan_repository import SqlAlchemyLoanRepository
from src.infrastructure.repositories.member_repository import SqlAlchemyMemberRepository


def create_dependencies(db_session):
    book_service = BookService(
        SqlAlchemyBookRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    member_service = MemberService(
        SqlAlchemyMemberRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    employee_service = EmployeeService(
        SqlAlchemyEmployeeRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    book = book_service.create_book(BookCreateRequest(title="DDD", author="Evans"))
    member = member_service.create_member(
        MemberCreateRequest(first_name="Julia", last_name="Diaz", email="julia.diaz@example.com")
    )
    employee = employee_service.create_employee(
        EmployeeCreateRequest(first_name="Mario", last_name="Soto", position="Librarian")
    )
    return book, member, employee


def test_create_loan_success(db_session):
    book, member, employee = create_dependencies(db_session)
    service = LoanService(
        SqlAlchemyLoanRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        SqlAlchemyMemberRepository(db_session),
        SqlAlchemyEmployeeRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )

    result = service.create_loan(
        LoanCreateRequest(
            book_copy_id=book.first_available_copy_id,
            member_id=member.member_id,
            employee_id=employee.employee_id,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14),
        )
    )

    assert result.status == "in_progress"
    assert result.book_copy_id == book.first_available_copy_id


def test_create_loan_rejects_unavailable_copy(db_session):
    book, member, employee = create_dependencies(db_session)
    service = LoanService(
        SqlAlchemyLoanRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        SqlAlchemyMemberRepository(db_session),
        SqlAlchemyEmployeeRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    payload = LoanCreateRequest(
        book_copy_id=book.first_available_copy_id,
        member_id=member.member_id,
        employee_id=employee.employee_id,
        loan_date=date.today(),
        due_date=date.today() + timedelta(days=14),
    )
    service.create_loan(payload)

    with pytest.raises(DomainError, match="Book copy is not available for loan."):
        service.create_loan(payload)


def test_return_loan_success(db_session):
    book, member, employee = create_dependencies(db_session)
    service = LoanService(
        SqlAlchemyLoanRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        SqlAlchemyMemberRepository(db_session),
        SqlAlchemyEmployeeRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    loan = service.create_loan(
        LoanCreateRequest(
            book_copy_id=book.first_available_copy_id,
            member_id=member.member_id,
            employee_id=employee.employee_id,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14),
        )
    )

    returned = service.return_loan(loan.loan_id, LoanReturnRequest())
    assert returned.status == "returned"
    assert returned.actual_return_date == date.today()


def test_return_loan_not_found(db_session):
    service = LoanService(
        SqlAlchemyLoanRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        SqlAlchemyMemberRepository(db_session),
        SqlAlchemyEmployeeRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    with pytest.raises(DomainError, match="Loan not found."):
        service.return_loan("missing-loan", LoanReturnRequest())
