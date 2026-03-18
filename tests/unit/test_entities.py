from datetime import date

from src.domain.entities.book import Book
from src.domain.entities.member import Member, MemberStatus
from src.domain.entities.loan import Loan, LoanStatus


def test_book_model_fields():
    book = Book(
        book_id="book-1",
        title="Test Book",
        author="Test Author",
        isbn="9780123456789",
        pages=200,
        max_loan_weeks=3,
        total_copies=2,
    )

    assert book.book_id == "book-1"
    assert book.title == "Test Book"
    assert book.total_copies == 2


def test_member_model_defaults():
    member = Member(
        member_id="member-1",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        registration_date=date.today(),
        status=MemberStatus.ACTIVE,
    )

    assert member.email == "john@example.com"
    assert member.status == MemberStatus.ACTIVE
    assert member.full_name == "John Doe"


def test_loan_status_values_are_canonical():
    loan = Loan(
        loan_id="loan-1",
        book_copy_id="copy-1",
        member_id="member-1",
        employee_id=None,
        loan_date=date.today(),
        due_date=date.today(),
        status=LoanStatus.IN_PROGRESS,
    )
    assert loan.status == LoanStatus.IN_PROGRESS
    assert LoanStatus.RETURNED.value == "returned"
    assert LoanStatus.OVERDUE.value == "overdue"
