import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, date, timedelta

from domain.entities.loan import Loan, LoanStatus
from domain.entities.book import BookCopy, BookStatus
from application.use_cases.loan_service import LoanService
from application.dto.loan_dto import CreateLoanRequest, ReturnLoanRequest


class MockLoanRepository:
    def __init__(self):
        self.loans = {}
        
    async def create_loan(self, loan: Loan) -> Loan:
        self.loans[loan.loan_id] = loan
        return loan
        
    async def get_loan_by_id(self, loan_id: str):
        return self.loans.get(loan_id)
        
    async def get_active_loans_by_book_copy_id(self, book_copy_id: str):
        return [loan for loan in self.loans.values() 
                if loan.book_copy_id == book_copy_id and loan.status == LoanStatus.IN_PROGRESS]
        
    async def update_loan(self, loan: Loan) -> Loan:
        self.loans[loan.loan_id] = loan
        return loan
        
    async def list_loans(self, limit: int = 50, last_key=None):
        loans = list(self.loans.values())[:limit]
        return loans, None


class MockBookCopyRepository:
    def __init__(self):
        self.copies = {}
        
    async def get_book_copy_by_id(self, book_copy_id: str):
        return self.copies.get(book_copy_id)
        
    async def update_book_copy(self, book_copy: BookCopy) -> BookCopy:
        self.copies[book_copy.book_copy_id] = book_copy
        return book_copy


@pytest.fixture
def loan_service():
    loan_repo = MockLoanRepository()
    book_copy_repo = MockBookCopyRepository()
    return LoanService(loan_repo, book_copy_repo), loan_repo, book_copy_repo


@pytest.mark.asyncio
async def test_create_loan_success(loan_service):
    service, loan_repo, book_copy_repo = loan_service
    
    # Setup available book copy
    book_copy = BookCopy(
        book_copy_id="book-1-001",
        book_id="book-1",
        status=BookStatus.AVAILABLE,
        created_at=datetime.utcnow()
    )
    book_copy_repo.copies["book-1-001"] = book_copy
    
    request = CreateLoanRequest(
        book_copy_id="book-1-001",
        member_id="member-1",
        employee_id="employee-1",
        loan_date=date.today(),
        due_date=date.today() + timedelta(weeks=3)
    )
    
    result = await service.create_loan(request)
    
    assert result.book_copy_id == "book-1-001"
    assert result.member_id == "member-1"
    assert result.employee_id == "employee-1"
    assert result.status == "Prestado"
    assert result.loan_date == date.today()
    
    # Check that book copy status was updated
    updated_copy = await book_copy_repo.get_book_copy_by_id("book-1-001")
    assert updated_copy.status == BookStatus.LOANED


@pytest.mark.asyncio
async def test_create_loan_book_not_available(loan_service):
    service, loan_repo, book_copy_repo = loan_service
    
    # Setup loaned book copy
    book_copy = BookCopy(
        book_copy_id="book-1-001",
        book_id="book-1",
        status=BookStatus.LOANED,
        created_at=datetime.utcnow()
    )
    book_copy_repo.copies["book-1-001"] = book_copy
    
    request = CreateLoanRequest(
        book_copy_id="book-1-001",
        member_id="member-1",
        loan_date=date.today(),
        due_date=date.today() + timedelta(weeks=3)
    )
    
    with pytest.raises(ValueError, match="Book copy is not available for loan"):
        await service.create_loan(request)


@pytest.mark.asyncio
async def test_create_loan_already_has_active_loan(loan_service):
    service, loan_repo, book_copy_repo = loan_service
    
    # Setup available book copy
    book_copy = BookCopy(
        book_copy_id="book-1-001",
        book_id="book-1",
        status=BookStatus.AVAILABLE,
        created_at=datetime.utcnow()
    )
    book_copy_repo.copies["book-1-001"] = book_copy
    
    # Create existing active loan
    existing_loan = Loan(
        loan_id="loan-1",
        book_copy_id="book-1-001",
        member_id="member-2",
        employee_id=None,
        loan_date=date.today(),
        due_date=date.today() + timedelta(weeks=3),
        status=LoanStatus.IN_PROGRESS,
        created_at=datetime.utcnow()
    )
    loan_repo.loans["loan-1"] = existing_loan
    
    request = CreateLoanRequest(
        book_copy_id="book-1-001",
        member_id="member-1",
        loan_date=date.today(),
        due_date=date.today() + timedelta(weeks=3)
    )
    
    with pytest.raises(ValueError, match="Book copy already has an active loan"):
        await service.create_loan(request)


@pytest.mark.asyncio
async def test_return_loan_success(loan_service):
    service, loan_repo, book_copy_repo = loan_service
    
    # Setup loan and book copy
    loan = Loan(
        loan_id="loan-1",
        book_copy_id="book-1-001",
        member_id="member-1",
        employee_id=None,
        loan_date=date.today() - timedelta(days=7),
        due_date=date.today() + timedelta(days=14),
        status=LoanStatus.IN_PROGRESS,
        created_at=datetime.utcnow()
    )
    loan_repo.loans["loan-1"] = loan
    
    book_copy = BookCopy(
        book_copy_id="book-1-001",
        book_id="book-1",
        status=BookStatus.LOANED,
        created_at=datetime.utcnow()
    )
    book_copy_repo.copies["book-1-001"] = book_copy
    
    request = ReturnLoanRequest()
    result = await service.return_loan("loan-1", request)
    
    assert result.status == "Disponible"
    assert result.actual_return_date == date.today()
    
    # Check that book copy status was updated
    updated_copy = await book_copy_repo.get_book_copy_by_id("book-1-001")
    assert updated_copy.status == BookStatus.AVAILABLE


@pytest.mark.asyncio
async def test_return_loan_not_found(loan_service):
    service, loan_repo, book_copy_repo = loan_service
    
    request = ReturnLoanRequest()
    
    with pytest.raises(ValueError, match="Loan not found"):
        await service.return_loan("non-existent", request)


@pytest.mark.asyncio
async def test_return_loan_already_returned(loan_service):
    service, loan_repo, book_copy_repo = loan_service
    
    # Setup already returned loan
    loan = Loan(
        loan_id="loan-1",
        book_copy_id="book-1-001",
        member_id="member-1",
        employee_id=None,
        loan_date=date.today() - timedelta(days=7),
        due_date=date.today() + timedelta(days=14),
        actual_return_date=date.today() - timedelta(days=1),
        status=LoanStatus.RETURNED,
        created_at=datetime.utcnow()
    )
    loan_repo.loans["loan-1"] = loan
    
    request = ReturnLoanRequest()
    
    with pytest.raises(ValueError, match="Loan already returned"):
        await service.return_loan("loan-1", request)
