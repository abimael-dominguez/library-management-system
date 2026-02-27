import pytest
from pydantic import ValidationError
from datetime import date

from application.dto.book_dto import CreateBookRequest, SearchBooksRequest, AutocompleteRequest
from application.dto.loan_dto import CreateLoanRequest, ReturnLoanRequest


def test_create_book_request_valid():
    request = CreateBookRequest(
        title="Test Book",
        author="Test Author",
        isbn="978-0123456789",
        publisher="Test Publisher",
        publication_year=2023,
        genre="Fiction",
        pages=300,
        max_loan_weeks=4,
        total_copies=3
    )
    
    assert request.title == "Test Book"
    assert request.author == "Test Author"
    assert request.isbn == "978-0123456789"
    assert request.max_loan_weeks == 4
    assert request.total_copies == 3


def test_create_book_request_minimal():
    request = CreateBookRequest(
        title="Minimal Book",
        author="Author Name"
    )
    
    assert request.title == "Minimal Book"
    assert request.author == "Author Name"
    assert request.max_loan_weeks == 3  # Default value
    assert request.total_copies == 1  # Default value


def test_create_book_request_invalid_title():
    with pytest.raises(ValidationError) as exc_info:
        CreateBookRequest(
            title="",  # Empty title
            author="Test Author"
        )
    
    assert "String should have at least 1 character" in str(exc_info.value)


def test_create_book_request_invalid_year():
    with pytest.raises(ValidationError) as exc_info:
        CreateBookRequest(
            title="Test Book",
            author="Test Author",
            publication_year=999  # Too early
        )
    
    assert "Input should be greater than or equal to 1000" in str(exc_info.value)


def test_search_books_request_valid():
    request = SearchBooksRequest(
        q="python programming",
        limit=20
    )
    
    assert request.q == "python programming"
    assert request.limit == 20


def test_search_books_request_invalid_query():
    with pytest.raises(ValidationError) as exc_info:
        SearchBooksRequest(
            q="",  # Empty query
            limit=10
        )
    
    assert "String should have at least 1 character" in str(exc_info.value)


def test_autocomplete_request_valid():
    request = AutocompleteRequest(
        q="py",
        type="book",
        limit=5
    )
    
    assert request.q == "py"
    assert request.type == "book"
    assert request.limit == 5


def test_autocomplete_request_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        AutocompleteRequest(
            q="py",
            type="invalid",  # Invalid type
            limit=5
        )
    
    assert "String should match pattern" in str(exc_info.value)


def test_create_loan_request_valid():
    request = CreateLoanRequest(
        book_copy_id="book-1-001",
        member_id="member-1",
        employee_id="employee-1",
        loan_date=date.today(),
        due_date=date(2024, 12, 31)
    )
    
    assert request.book_copy_id == "book-1-001"
    assert request.member_id == "member-1"
    assert request.employee_id == "employee-1"


def test_create_loan_request_minimal():
    from datetime import date
    request = CreateLoanRequest(
        book_copy_id="book-1-001",
        member_id="member-1",
        loan_date=date.today(),
        due_date=date.today()
    )
    
    assert request.book_copy_id == "book-1-001"
    assert request.member_id == "member-1"
    assert request.employee_id is None
    assert request.loan_date == date.today()
    assert request.due_date == date.today()


def test_create_loan_request_invalid():
    with pytest.raises(ValidationError) as exc_info:
        CreateLoanRequest(
            book_copy_id="",  # Empty book_copy_id
            member_id="member-1"
        )
    
    assert "String should have at least 1 character" in str(exc_info.value)


def test_return_loan_request():
    request = ReturnLoanRequest(
        actual_return_date=date.today()
    )
    
    assert request.actual_return_date == date.today()
    
    # Test with no date (should use default)
    request_no_date = ReturnLoanRequest()
    assert request_no_date.actual_return_date is None