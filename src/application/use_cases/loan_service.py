"""
Loan Service - Fast Loan/Return Workflow Use Cases
"""

from typing import List, Optional
from datetime import date, datetime
from ...domain.repositories.loan_repository import LoanRepository
from ...domain.repositories.book_repository import BookRepository, BookCopyRepository
from ...domain.repositories.member_repository import MemberRepository, EmployeeRepository
from ...domain.entities.loan import Loan, LoanSummary, LoanStatus
from ...shared.exceptions import ValidationError, BookNotFoundError, MemberNotFoundError

class LoanService:
    """Service for handling loan operations with optimized workflow"""
    
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository,
        book_copy_repository: BookCopyRepository,
        member_repository: MemberRepository,
        employee_repository: EmployeeRepository
    ):
        self.loan_repository = loan_repository
        self.book_repository = book_repository
        self.book_copy_repository = book_copy_repository
        self.member_repository = member_repository
        self.employee_repository = employee_repository
    
    async def create_loan(
        self,
        book_id: str,
        member_id: str,
        employee_id: Optional[str] = None,
        loan_weeks: int = 2
    ) -> Loan:
        """Create a new loan (Préstamo) with validation and status updates"""
        
        # 1. Validate member exists and is active
        member = await self.member_repository.get_member_by_id(member_id)
        if not member:
            raise MemberNotFoundError(f"Member {member_id} not found")
        if not member.is_active():
            raise ValidationError(f"Member {member.get_full_name()} is not active")
        
        # 2. Get book and validate availability
        book_with_copies = await self.book_repository.get_book_with_copies(book_id)
        if not book_with_copies:
            raise BookNotFoundError(f"Book {book_id} not found")
        
        book = book_with_copies['book']
        available_copies = [c for c in book_with_copies['copies'] if c.is_available()]
        
        if not available_copies:
            raise ValidationError(f"No available copies of '{book.title}'")
        
        # 3. Get employee info if provided
        employee_name = None
        if employee_id:
            employee = await self.employee_repository.get_employee_by_id(employee_id)
            if employee:
                employee_name = employee.get_full_name()
        
        # 4. Select first available copy
        selected_copy = available_copies[0]
        
        # 5. Create loan
        loan = Loan.create_new_loan(
            copy_id=selected_copy.id,
            book_id=book.id,
            book_title=book.title,
            member_id=member.id,
            member_name=member.get_full_name(),
            employee_id=employee_id,
            employee_name=employee_name,
            loan_weeks=loan_weeks
        )
        
        # 6. Save loan
        created_loan = await self.loan_repository.create_loan(loan)
        
        # 7. Update copy status to loaned
        await self.book_copy_repository.update_copy_status(selected_copy.id, 'loaned')
        
        # 8. Update book available copies count
        await self.book_repository.update_available_copies(book.id, -1)
        
        return created_loan
    
    async def return_book(
        self,
        loan_id: str,
        return_date: Optional[date] = None
    ) -> Loan:
        """Return a book (Devolución) with status updates"""
        
        # 1. Get loan
        loan = await self.loan_repository.get_loan_by_id(loan_id)
        if not loan:
            raise ValidationError(f"Loan {loan_id} not found")
        
        if loan.status == LoanStatus.RETURNED:
            raise ValidationError("Book already returned")
        
        # 2. Return the book
        returned_loan = await self.loan_repository.return_book(loan_id, return_date)
        
        # 3. Update copy status to available
        await self.book_copy_repository.update_copy_status(loan.copy_id, 'available')
        
        # 4. Update book available copies count
        await self.book_repository.update_available_copies(loan.book_id, +1)
        
        return returned_loan
    
    async def extend_loan(self, loan_id: str, weeks: int = 1) -> Loan:
        """Extend loan due date"""
        loan = await self.loan_repository.get_loan_by_id(loan_id)
        if not loan:
            raise ValidationError(f"Loan {loan_id} not found")
        
        if loan.status != LoanStatus.IN_PROGRESS:
            raise ValidationError("Can only extend active loans")
        
        return await self.loan_repository.extend_loan(loan_id, weeks)
    
    async def get_member_loans(
        self,
        member_id: str,
        status: Optional[LoanStatus] = None
    ) -> List[LoanSummary]:
        """Get loans for a specific member"""
        return await self.loan_repository.get_loans_by_member(member_id, status)
    
    async def get_active_loans(self, limit: int = 50) -> List[LoanSummary]:
        """Get all active loans"""
        return await self.loan_repository.get_active_loans(limit)
    
    async def get_overdue_loans(self, limit: int = 50) -> List[LoanSummary]:
        """Get overdue loans (critical for library operations)"""
        return await self.loan_repository.get_overdue_loans(limit)
    
    async def get_loan_statistics(self) -> dict:
        """Get loan statistics for dashboard"""
        stats = await self.loan_repository.get_loan_statistics()
        
        # Add calculated metrics
        overdue_loans = await self.get_overdue_loans(100)  # Get more for accurate count
        active_loans = await self.get_active_loans(100)
        
        stats.update({
            'overdue_count': len(overdue_loans),
            'active_count': len(active_loans),
            'overdue_percentage': round(
                (len(overdue_loans) / len(active_loans) * 100) if active_loans else 0, 1
            )
        })
        
        return stats
    
    async def bulk_return_books(self, loan_ids: List[str]) -> dict:
        """Return multiple books at once"""
        results = {
            'successful': [],
            'failed': [],
            'total_processed': len(loan_ids)
        }
        
        for loan_id in loan_ids:
            try:
                returned_loan = await self.return_book(loan_id)
                results['successful'].append({
                    'loan_id': loan_id,
                    'book_title': returned_loan.book_title,
                    'member_name': returned_loan.member_name
                })
            except Exception as e:
                results['failed'].append({
                    'loan_id': loan_id,
                    'error': str(e)
                })
        
        results['success_rate'] = round(
            (len(results['successful']) / len(loan_ids) * 100) if loan_ids else 0, 1
        )
        
        return results