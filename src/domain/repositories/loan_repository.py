"""
Loan Repository Interface - Abstract Contract for Loan Operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from ..entities.loan import Loan, LoanSummary, LoanStatus

class LoanRepository(ABC):
    """Abstract repository interface for loan operations"""
    
    @abstractmethod
    async def create_loan(self, loan: Loan) -> Loan:
        """Create a new loan"""
        pass
    
    @abstractmethod
    async def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        """Get loan by ID"""
        pass
    
    @abstractmethod
    async def update_loan(self, loan: Loan) -> Loan:
        """Update existing loan"""
        pass
    
    @abstractmethod
    async def return_book(self, loan_id: str, return_date: Optional[date] = None) -> Loan:
        """Mark book as returned"""
        pass
    
    @abstractmethod
    async def extend_loan(self, loan_id: str, weeks: int = 1) -> Loan:
        """Extend loan due date"""
        pass
    
    @abstractmethod
    async def get_loans_by_member(self, member_id: str, status: Optional[LoanStatus] = None) -> List[LoanSummary]:
        """Get loans for a specific member"""
        pass
    
    @abstractmethod
    async def get_active_loans(self, limit: int = 50) -> List[LoanSummary]:
        """Get all active loans"""
        pass
    
    @abstractmethod
    async def get_overdue_loans(self, limit: int = 50) -> List[LoanSummary]:
        """Get overdue loans (critical for library operations)"""
        pass
    
    @abstractmethod
    async def get_loans_by_book(self, book_id: str) -> List[LoanSummary]:
        """Get loan history for a book"""
        pass
    
    @abstractmethod
    async def get_loans_by_copy(self, copy_id: str) -> List[LoanSummary]:
        """Get loan history for a specific copy"""
        pass
    
    @abstractmethod
    async def get_loans_by_date_range(self, start_date: date, end_date: date) -> List[LoanSummary]:
        """Get loans within date range"""
        pass
    
    @abstractmethod
    async def get_loan_statistics(self) -> dict:
        """Get loan statistics for dashboard"""
        pass