"""Entity-to-DTO serialisation helpers.

These pure functions live in the infrastructure API layer because they
translate domain entities into Pydantic response DTOs that the HTTP
handlers return to clients.
"""

from __future__ import annotations

from ...application.dtos.book_dto import BookResponse
from ...application.dtos.employee_dto import EmployeeResponse
from ...application.dtos.loan_dto import LoanResponse
from ...application.dtos.member_dto import MemberResponse
from ...domain.entities.book import Book
from ...domain.entities.employee import Employee
from ...domain.entities.loan import Loan
from ...domain.entities.member import Member


def serialize_book(book: Book) -> BookResponse:
    return BookResponse(
        book_id=book.book_id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        publisher=book.publisher,
        publication_year=book.publication_year,
        genre=book.genre,
        pages=book.pages,
        max_loan_weeks=book.max_loan_weeks,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        first_available_copy_id=book.first_available_copy_id,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


def serialize_member(member: Member) -> MemberResponse:
    return MemberResponse(
        member_id=member.member_id,
        first_name=member.first_name,
        last_name=member.last_name,
        email=member.email,
        address=member.address,
        phone=member.phone,
        registration_date=member.registration_date,
        status=member.status.value,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )


def serialize_employee(employee: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        employee_id=employee.employee_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        position=employee.position,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
    )


def serialize_loan(loan: Loan) -> LoanResponse:
    return LoanResponse(
        loan_id=loan.loan_id,
        book_copy_id=loan.book_copy_id,
        member_id=loan.member_id,
        employee_id=loan.employee_id,
        loan_date=loan.loan_date,
        due_date=loan.due_date,
        actual_return_date=loan.actual_return_date,
        status=loan.status.value,
        book_title=loan.book_title,
        book_author=loan.book_author,
        member_name=loan.member_name,
        employee_name=loan.employee_name,
        created_at=loan.created_at,
        updated_at=loan.updated_at,
    )
