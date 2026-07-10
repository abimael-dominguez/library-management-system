from datetime import date, timedelta

import pytest
from sqlalchemy import select

from src.application.dtos.book_dto import BookCreateRequest
from src.application.dtos.employee_dto import EmployeeCreateRequest
from src.application.dtos.loan_dto import LoanCreateRequest, LoanReturnRequest
from src.application.dtos.member_dto import MemberCreateRequest
from src.application.use_cases.create_book import CreateBookUseCase
from src.application.use_cases.create_employee import CreateEmployeeUseCase
from src.application.use_cases.create_loan import CreateLoanUseCase
from src.application.use_cases.create_member import CreateMemberUseCase
from src.application.use_cases.get_loan import GetLoanUseCase
from src.application.use_cases.return_loan import ReturnLoanUseCase
from src.domain.exceptions import DomainError
from src.infrastructure.adapters.book_repository import SqlAlchemyBookCopyRepository, SqlAlchemyBookRepository
from src.infrastructure.adapters.employee_repository import SqlAlchemyEmployeeRepository
from src.infrastructure.adapters.loan_repository import SqlAlchemyLoanRepository
from src.infrastructure.adapters.member_repository import SqlAlchemyMemberRepository
from src.infrastructure.adapters.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.persistence.models import BookCopyModel


def _build_repos(db_session):
    """Return all repository and UoW instances for a given session."""
    return {
        "book_repo": SqlAlchemyBookRepository(db_session),
        "book_copy_repo": SqlAlchemyBookCopyRepository(db_session),
        "member_repo": SqlAlchemyMemberRepository(db_session),
        "employee_repo": SqlAlchemyEmployeeRepository(db_session),
        "loan_repo": SqlAlchemyLoanRepository(db_session),
        "uow": SqlAlchemyUnitOfWork(db_session),
    }


def create_dependencies(db_session):
    repos = _build_repos(db_session)
    create_book = CreateBookUseCase(
        book_repo=repos["book_repo"],
        book_copy_repo=repos["book_copy_repo"],
        unit_of_work=repos["uow"],
    )
    create_member = CreateMemberUseCase(
        member_repo=repos["member_repo"],
        unit_of_work=repos["uow"],
    )
    create_employee = CreateEmployeeUseCase(
        employee_repo=repos["employee_repo"],
        unit_of_work=repos["uow"],
    )
    book = create_book.execute(payload=BookCreateRequest(title="DDD", author="Evans"))
    member = create_member.execute(
        payload=MemberCreateRequest(first_name="Julia", last_name="Diaz", email="julia.diaz@example.com")
    )
    employee = create_employee.execute(
        payload=EmployeeCreateRequest(first_name="Mario", last_name="Soto", position="Librarian")
    )
    return book, member, employee


def test_create_loan_success(db_session):
    book, member, employee = create_dependencies(db_session)
    repos = _build_repos(db_session)
    create_loan = CreateLoanUseCase(
        loan_repo=repos["loan_repo"],
        book_copy_repo=repos["book_copy_repo"],
        member_repo=repos["member_repo"],
        employee_repo=repos["employee_repo"],
        unit_of_work=repos["uow"],
    )

    result = create_loan.execute(
        payload=LoanCreateRequest(
            book_copy_id=book.first_available_copy_id,
            member_id=member.member_id,
            employee_id=employee.employee_id,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14),
        )
    )

    assert result.status == "in_progress"
    assert result.book_copy_id == book.first_available_copy_id

    copy = db_session.scalar(select(BookCopyModel).where(BookCopyModel.book_copy_id == result.book_copy_id))
    assert copy is not None
    assert copy.status == "available"


def test_create_loan_rejects_unavailable_copy(db_session):
    book, member, employee = create_dependencies(db_session)
    repos = _build_repos(db_session)
    create_loan = CreateLoanUseCase(
        loan_repo=repos["loan_repo"],
        book_copy_repo=repos["book_copy_repo"],
        member_repo=repos["member_repo"],
        employee_repo=repos["employee_repo"],
        unit_of_work=repos["uow"],
    )
    payload = LoanCreateRequest(
        book_copy_id=book.first_available_copy_id,
        member_id=member.member_id,
        employee_id=employee.employee_id,
        loan_date=date.today(),
        due_date=date.today() + timedelta(days=14),
    )
    create_loan.execute(payload=payload)

    with pytest.raises(DomainError, match="Book copy already has an active loan."):
        create_loan.execute(payload=payload)


def test_return_loan_success(db_session):
    book, member, employee = create_dependencies(db_session)
    repos = _build_repos(db_session)
    create_loan = CreateLoanUseCase(
        loan_repo=repos["loan_repo"],
        book_copy_repo=repos["book_copy_repo"],
        member_repo=repos["member_repo"],
        employee_repo=repos["employee_repo"],
        unit_of_work=repos["uow"],
    )
    return_loan_uc = ReturnLoanUseCase(
        loan_repo=repos["loan_repo"],
        book_copy_repo=repos["book_copy_repo"],
        unit_of_work=repos["uow"],
    )
    get_loan = GetLoanUseCase(loan_repo=repos["loan_repo"])

    loan = create_loan.execute(
        payload=LoanCreateRequest(
            book_copy_id=book.first_available_copy_id,
            member_id=member.member_id,
            employee_id=employee.employee_id,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14),
        )
    )

    returned = return_loan_uc.execute(loan_id=loan.loan_id, payload=LoanReturnRequest())
    assert returned.status == "returned"
    assert returned.actual_return_date == date.today()

    reloaded = get_loan.execute(loan_id=loan.loan_id)
    assert reloaded is not None
    assert reloaded.status == "returned"
    assert reloaded.actual_return_date == date.today()


def test_returned_loan_allows_new_loan_for_same_copy(db_session):
    book, member, employee = create_dependencies(db_session)
    repos = _build_repos(db_session)
    create_loan = CreateLoanUseCase(
        loan_repo=repos["loan_repo"],
        book_copy_repo=repos["book_copy_repo"],
        member_repo=repos["member_repo"],
        employee_repo=repos["employee_repo"],
        unit_of_work=repos["uow"],
    )
    return_loan_uc = ReturnLoanUseCase(
        loan_repo=repos["loan_repo"],
        book_copy_repo=repos["book_copy_repo"],
        unit_of_work=repos["uow"],
    )

    first = create_loan.execute(
        payload=LoanCreateRequest(
            book_copy_id=book.first_available_copy_id,
            member_id=member.member_id,
            employee_id=employee.employee_id,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14),
        )
    )

    return_loan_uc.execute(loan_id=first.loan_id, payload=LoanReturnRequest())

    second = create_loan.execute(
        payload=LoanCreateRequest(
            book_copy_id=book.first_available_copy_id,
            member_id=member.member_id,
            employee_id=employee.employee_id,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )
    )

    assert second.status == "in_progress"


def test_return_loan_not_found(db_session):
    repos = _build_repos(db_session)
    return_loan_uc = ReturnLoanUseCase(
        loan_repo=repos["loan_repo"],
        book_copy_repo=repos["book_copy_repo"],
        unit_of_work=repos["uow"],
    )
    with pytest.raises(DomainError, match="Loan not found."):
        return_loan_uc.execute(loan_id="missing-loan", payload=LoanReturnRequest())
