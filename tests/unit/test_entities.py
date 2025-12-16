import pytest
from datetime import datetime, date
from src.domain.entities.book import Book, BookCopy, BookStatus
from src.domain.entities.member import Member, MemberStatus
from src.domain.entities.loan import Loan, LoanStatus


def test_book_entity():
    book = Book(
        book_id="test-id",
        title="Test Book",
        author="Test Author",
        isbn="978-0123456789",
        pages=200,
        max_loan_weeks=3,
        total_copies=2
    )
    
    assert book.book_id == "test-id"
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.isbn == "978-0123456789"
    assert book.pages == 200
    assert book.max_loan_weeks == 3
    assert book.total_copies == 2


def test_book_copy_entity():
    book_copy = BookCopy(
        book_copy_id="book-1-001",
        book_id="book-1",
        status=BookStatus.AVAILABLE
    )
    
    assert book_copy.book_copy_id == "book-1-001"
    assert book_copy.book_id == "book-1"
    assert book_copy.status == BookStatus.AVAILABLE


def test_member_entity():
    member = Member(
        member_id="member-1",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="555-1234",
        status=MemberStatus.ACTIVE
    )
    
    assert member.member_id == "member-1"
    assert member.first_name == "John"
    assert member.last_name == "Doe"
    assert member.email == "john.doe@example.com"
    assert member.full_name == "John Doe"
    assert member.status == MemberStatus.ACTIVE


def test_loan_entity():
    loan_date = date.today()
    due_date = date(2024, 12, 31)
    
    loan = Loan(
        loan_id="loan-1",
        book_copy_id="book-1-001",
        member_id="member-1",
        employee_id="employee-1",
        loan_date=loan_date,
        due_date=due_date,
        status=LoanStatus.IN_PROGRESS
    )
    
    assert loan.loan_id == "loan-1"
    assert loan.book_copy_id == "book-1-001"
    assert loan.member_id == "member-1"
    assert loan.employee_id == "employee-1"
    assert loan.loan_date == loan_date
    assert loan.due_date == due_date
    assert loan.status == LoanStatus.IN_PROGRESS


def test_loan_is_overdue():
    # Not overdue loan
    loan = Loan(
        loan_id="loan-1",
        book_copy_id="book-1-001",
        member_id="member-1",
        employee_id=None,
        loan_date=date.today(),
        due_date=date(2025, 12, 31),  # Future date
        status=LoanStatus.IN_PROGRESS
    )
    assert not loan.is_overdue
    
    # Overdue loan
    overdue_loan = Loan(
        loan_id="loan-2",
        book_copy_id="book-1-002",
        member_id="member-1",
        employee_id=None,
        loan_date=date(2024, 1, 1),
        due_date=date(2024, 1, 15),  # Past date
        status=LoanStatus.IN_PROGRESS
    )
    assert overdue_loan.is_overdue
    
    # Returned loan (not overdue even if past due date)
    returned_loan = Loan(
        loan_id="loan-3",
        book_copy_id="book-1-003",
        member_id="member-1",
        employee_id=None,
        loan_date=date(2024, 1, 1),
        due_date=date(2024, 1, 15),  # Past date
        actual_return_date=date(2024, 1, 10),
        status=LoanStatus.RETURNED
    )
    assert not returned_loan.is_overdue