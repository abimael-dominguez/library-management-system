"""Composition root — assembles use cases with their concrete dependencies.

This module is the **only** place where concrete adapter classes are
instantiated and wired into application-layer use cases.  Changing a
persistence backend or swapping a service implementation requires edits
here and nowhere else.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ...application.use_cases.autocomplete_members import AutocompleteMembersUseCase
from ...application.use_cases.create_book import CreateBookUseCase
from ...application.use_cases.create_employee import CreateEmployeeUseCase
from ...application.use_cases.create_loan import CreateLoanUseCase
from ...application.use_cases.create_member import CreateMemberUseCase
from ...application.use_cases.get_book import GetBookUseCase
from ...application.use_cases.get_loan import GetLoanUseCase
from ...application.use_cases.list_books import ListBooksUseCase
from ...application.use_cases.list_employees import ListEmployeesUseCase
from ...application.use_cases.list_loans import ListLoansUseCase
from ...application.use_cases.list_members import ListMembersUseCase
from ...application.use_cases.return_loan import ReturnLoanUseCase
from ...application.use_cases.search_books import SearchBooksUseCase
from ..adapters.book_repository import SqlAlchemyBookCopyRepository, SqlAlchemyBookRepository
from ..adapters.employee_repository import SqlAlchemyEmployeeRepository
from ..adapters.loan_repository import SqlAlchemyLoanRepository
from ..adapters.member_repository import SqlAlchemyMemberRepository
from ..adapters.unit_of_work import SqlAlchemyUnitOfWork


class ServiceContainer:
    """Holds fully-wired use-case instances for a single request scope.

    Create one ``ServiceContainer`` per database session (i.e. per HTTP
    request) so that every use case shares the same transactional context.
    """

    def __init__(self, session: Session) -> None:
        unit_of_work = SqlAlchemyUnitOfWork(session)

        book_repo = SqlAlchemyBookRepository(session)
        book_copy_repo = SqlAlchemyBookCopyRepository(session)
        member_repo = SqlAlchemyMemberRepository(session)
        employee_repo = SqlAlchemyEmployeeRepository(session)
        loan_repo = SqlAlchemyLoanRepository(session)

        # Book use cases
        self.list_books = ListBooksUseCase(book_repo=book_repo, book_copy_repo=book_copy_repo)
        self.get_book = GetBookUseCase(book_repo=book_repo, book_copy_repo=book_copy_repo)
        self.search_books = SearchBooksUseCase(book_repo=book_repo, book_copy_repo=book_copy_repo)
        self.create_book = CreateBookUseCase(
            book_repo=book_repo, book_copy_repo=book_copy_repo, unit_of_work=unit_of_work,
        )

        # Member use cases
        self.list_members = ListMembersUseCase(member_repo=member_repo)
        self.create_member = CreateMemberUseCase(member_repo=member_repo, unit_of_work=unit_of_work)
        self.autocomplete_members = AutocompleteMembersUseCase(member_repo=member_repo)

        # Employee use cases
        self.list_employees = ListEmployeesUseCase(employee_repo=employee_repo)
        self.create_employee = CreateEmployeeUseCase(
            employee_repo=employee_repo, unit_of_work=unit_of_work,
        )

        # Loan use cases
        self.list_loans = ListLoansUseCase(loan_repo=loan_repo)
        self.get_loan = GetLoanUseCase(loan_repo=loan_repo)
        self.create_loan = CreateLoanUseCase(
            loan_repo=loan_repo,
            book_copy_repo=book_copy_repo,
            member_repo=member_repo,
            employee_repo=employee_repo,
            unit_of_work=unit_of_work,
        )
        self.return_loan = ReturnLoanUseCase(
            loan_repo=loan_repo, book_copy_repo=book_copy_repo, unit_of_work=unit_of_work,
        )
