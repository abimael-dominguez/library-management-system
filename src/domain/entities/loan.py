"""
Loan Domain Entity - Optimized for Fast Workflow and Status Tracking
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date, timedelta
from enum import Enum

class LoanStatus(str, Enum):
    """Loan status enumeration"""
    IN_PROGRESS = "in_progress"
    RETURNED = "returned"
    OVERDUE = "overdue"

class Loan(BaseModel):
    """Loan entity optimized for fast loan/return workflow"""
    
    id: str = Field(description="Unique loan identifier")
    copy_id: str = Field(description="Book copy being loaned")
    book_id: str = Field(description="Book reference for denormalization")
    book_title: str = Field(description="Book title (denormalized for UX)")
    member_id: str = Field(description="Member borrowing the book")
    member_name: str = Field(description="Member name (denormalized for UX)")
    employee_id: Optional[str] = Field(None, description="Employee processing the loan")
    employee_name: Optional[str] = Field(None, description="Employee name (denormalized)")
    loan_date: date = Field(default_factory=date.today, description="Date book was loaned")
    due_date: date = Field(description="Date book should be returned")
    return_date: Optional[date] = Field(None, description="Actual return date")
    status: LoanStatus = Field(default=LoanStatus.IN_PROGRESS, description="Current loan status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('due_date')
    def due_date_must_be_future(cls, v, values):
        """Ensure due date is after loan date"""
        loan_date = values.get('loan_date', date.today())
        if v <= loan_date:
            raise ValueError('Due date must be after loan date')
        return v
    
    @validator('return_date')
    def return_date_validation(cls, v, values):
        """Validate return date if provided"""
        if v:
            loan_date = values.get('loan_date', date.today())
            if v < loan_date:
                raise ValueError('Return date cannot be before loan date')
        return v
    
    @validator('status')
    def update_status_based_on_dates(cls, v, values):
        """Auto-update status based on dates"""
        return_date = values.get('return_date')
        due_date = values.get('due_date')
        
        if return_date:
            return LoanStatus.RETURNED
        elif due_date and due_date < date.today():
            return LoanStatus.OVERDUE
        else:
            return LoanStatus.IN_PROGRESS
    
    def is_overdue(self) -> bool:
        """Check if loan is overdue"""
        return self.status == LoanStatus.OVERDUE or (
            self.status == LoanStatus.IN_PROGRESS and 
            self.due_date < date.today()
        )
    
    def days_overdue(self) -> int:
        """Calculate days overdue (0 if not overdue)"""
        if not self.is_overdue():
            return 0
        return (date.today() - self.due_date).days
    
    def return_book(self, return_date: Optional[date] = None) -> 'Loan':
        """Mark book as returned"""
        self.return_date = return_date or date.today()
        self.status = LoanStatus.RETURNED
        self.updated_at = datetime.utcnow()
        return self
    
    def extend_due_date(self, weeks: int = 1) -> 'Loan':
        """Extend the due date by specified weeks"""
        if self.status != LoanStatus.IN_PROGRESS:
            raise ValueError("Can only extend active loans")
        
        self.due_date = self.due_date + timedelta(weeks=weeks)
        self.updated_at = datetime.utcnow()
        
        # Update status if no longer overdue
        if self.due_date >= date.today():
            self.status = LoanStatus.IN_PROGRESS
            
        return self
    
    def get_status_sort_key(self) -> str:
        """Get sort key for status-based queries"""
        if self.status == LoanStatus.IN_PROGRESS:
            return f"in_progress#{self.due_date.isoformat()}"
        elif self.status == LoanStatus.OVERDUE:
            return f"overdue#{self.due_date.isoformat()}"
        else:
            return f"returned#{self.return_date.isoformat() if self.return_date else self.loan_date.isoformat()}"
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format (cost-optimized with denormalization)"""
        return {
            'PK': f'L#{self.id}',
            'SK': f'L#{self.id}',
            'Type': 'LOAN',
            'Id': self.id,
            'CopyId': self.copy_id,
            'BookId': self.book_id,
            'BookTitle': self.book_title,  # Denormalized for fast display
            'MemberId': self.member_id,
            'MemberName': self.member_name,  # Denormalized for fast display
            'EmployeeId': self.employee_id,
            'EmployeeName': self.employee_name,
            'LoanDate': self.loan_date.isoformat(),
            'DueDate': self.due_date.isoformat(),
            'ReturnDate': self.return_date.isoformat() if self.return_date else None,
            'Status': self.status.value,
            'Created': self.created_at.isoformat() if self.created_at else None,
            'Updated': self.updated_at.isoformat() if self.updated_at else None,
            # GSI1 for status-based queries (overdue loans, etc.)
            'GSI1PK': 'STATUS',
            'GSI1SK': self.get_status_sort_key()
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Loan':
        """Create Loan from DynamoDB item"""
        return cls(
            id=item['Id'],
            copy_id=item['CopyId'],
            book_id=item['BookId'],
            book_title=item['BookTitle'],
            member_id=item['MemberId'],
            member_name=item['MemberName'],
            employee_id=item.get('EmployeeId'),
            employee_name=item.get('EmployeeName'),
            loan_date=date.fromisoformat(item['LoanDate']),
            due_date=date.fromisoformat(item['DueDate']),
            return_date=date.fromisoformat(item['ReturnDate']) if item.get('ReturnDate') else None,
            status=LoanStatus(item['Status']),
            created_at=datetime.fromisoformat(item['Created'].replace('Z', '+00:00')) if item.get('Created') else None,
            updated_at=datetime.fromisoformat(item['Updated'].replace('Z', '+00:00')) if item.get('Updated') else None
        )
    
    @classmethod
    def create_new_loan(
        cls,
        copy_id: str,
        book_id: str,
        book_title: str,
        member_id: str,
        member_name: str,
        employee_id: Optional[str] = None,
        employee_name: Optional[str] = None,
        loan_weeks: int = 2
    ) -> 'Loan':
        """Factory method to create a new loan"""
        import uuid
        
        loan_id = str(uuid.uuid4())[:8]
        due_date = date.today() + timedelta(weeks=loan_weeks)
        
        return cls(
            id=loan_id,
            copy_id=copy_id,
            book_id=book_id,
            book_title=book_title,
            member_id=member_id,
            member_name=member_name,
            employee_id=employee_id,
            employee_name=employee_name,
            due_date=due_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z',
            date: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True
        use_enum_values = True

class LoanSummary(BaseModel):
    """Optimized model for loan listings and reports"""
    
    id: str
    book_title: str
    member_name: str
    loan_date: date
    due_date: date
    return_date: Optional[date]
    status: LoanStatus
    days_overdue: int = 0
    
    @validator('days_overdue', always=True)
    def calculate_overdue_days(cls, v, values):
        """Calculate overdue days"""
        status = values.get('status')
        due_date = values.get('due_date')
        return_date = values.get('return_date')
        
        if return_date or status == LoanStatus.RETURNED:
            return 0
        elif due_date and due_date < date.today():
            return (date.today() - due_date).days
        return 0
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }
        use_enum_values = True