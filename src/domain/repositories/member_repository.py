"""
Member Repository Interface - Abstract Contract for Member Data Access
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.member import Member, Employee, MemberSearchResult, EmployeeSearchResult

class MemberRepository(ABC):
    """Abstract repository interface for member operations"""
    
    @abstractmethod
    async def create_member(self, member: Member) -> Member:
        """Create a new member"""
        pass
    
    @abstractmethod
    async def get_member_by_id(self, member_id: str) -> Optional[Member]:
        """Get member by ID"""
        pass
    
    @abstractmethod
    async def get_member_by_email(self, email: str) -> Optional[Member]:
        """Get member by email address"""
        pass
    
    @abstractmethod
    async def search_members(self, query: str, limit: int = 10) -> List[MemberSearchResult]:
        """Search members for autocomplete"""
        pass
    
    @abstractmethod
    async def update_member(self, member: Member) -> Member:
        """Update existing member"""
        pass
    
    @abstractmethod
    async def update_member_status(self, member_id: str, status: str) -> bool:
        """Update member status (active, inactive, suspended)"""
        pass
    
    @abstractmethod
    async def list_members(self, limit: int = 50, last_key: Optional[str] = None) -> dict:
        """List members with pagination"""
        pass
    
    @abstractmethod
    async def get_active_members(self, limit: int = 50) -> List[Member]:
        """Get all active members"""
        pass

class EmployeeRepository(ABC):
    """Abstract repository interface for employee operations"""
    
    @abstractmethod
    async def create_employee(self, employee: Employee) -> Employee:
        """Create a new employee"""
        pass
    
    @abstractmethod
    async def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        pass
    
    @abstractmethod
    async def search_employees(self, query: str, limit: int = 10) -> List[EmployeeSearchResult]:
        """Search employees for selection"""
        pass
    
    @abstractmethod
    async def update_employee(self, employee: Employee) -> Employee:
        """Update existing employee"""
        pass
    
    @abstractmethod
    async def list_employees(self) -> List[Employee]:
        """List all employees (small dataset)"""
        pass