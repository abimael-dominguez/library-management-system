"""
Member Domain Entity - Optimized for Search and UX
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime, date

class Member(BaseModel):
    """Member entity optimized for DynamoDB and search UX"""
    
    id: str = Field(description="Unique member identifier")
    first_name: str = Field(max_length=100, description="Member first name")
    last_name: str = Field(max_length=100, description="Member last name")
    email: EmailStr = Field(description="Member email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    address: Optional[str] = Field(None, max_length=255, description="Mailing address")
    status: str = Field(default='active', regex='^(active|inactive|suspended)$', description="Member status")
    registration_date: date = Field(default_factory=date.today, description="Registration date")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('first_name', 'last_name')
    def strip_names(cls, v):
        """Remove extra whitespace from names"""
        return v.strip() if v else v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Basic phone validation"""
        if v:
            # Remove common separators
            cleaned = ''.join(c for c in v if c.isdigit() or c in '+- ()')
            return cleaned.strip()
        return v
    
    def get_full_name(self) -> str:
        """Get formatted full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_search_key(self) -> str:
        """Get search key for autocomplete"""
        return f"{self.get_full_name()}#{self.email}"
    
    def is_active(self) -> bool:
        """Check if member can borrow books"""
        return self.status == 'active'
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format (cost-optimized)"""
        return {
            'PK': f'M#{self.id}',
            'SK': f'M#{self.id}',
            'Type': 'MEMBER',
            'Id': self.id,
            'FN': self.first_name,  # Shortened for cost
            'LN': self.last_name,
            'Email': str(self.email),
            'Phone': self.phone,
            'Addr': self.address,
            'Status': self.status,
            'RegDate': self.registration_date.isoformat(),
            'Created': self.created_at.isoformat() if self.created_at else None,
            'Updated': self.updated_at.isoformat() if self.updated_at else None,
            # GSI1 for member search
            'GSI1PK': 'SEARCH',
            'GSI1SK': self.get_search_key()
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Member':
        """Create Member from DynamoDB item"""
        return cls(
            id=item['Id'],
            first_name=item['FN'],
            last_name=item['LN'],
            email=item['Email'],
            phone=item.get('Phone'),
            address=item.get('Addr'),
            status=item['Status'],
            registration_date=date.fromisoformat(item['RegDate']),
            created_at=datetime.fromisoformat(item['Created'].replace('Z', '+00:00')) if item.get('Created') else None,
            updated_at=datetime.fromisoformat(item['Updated'].replace('Z', '+00:00')) if item.get('Updated') else None
        )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z',
            date: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True

class MemberSearchResult(BaseModel):
    """Optimized model for member autocomplete results"""
    
    id: str
    full_name: str
    email: str
    status: str
    
    @validator('full_name')
    def strip_name(cls, v):
        return v.strip()
    
    class Config:
        # Ultra-fast serialization for autocomplete
        json_encoders = {
            str: lambda v: v.strip() if v else None
        }

class Employee(BaseModel):
    """Employee entity for library staff"""
    
    id: str = Field(description="Unique employee identifier")
    first_name: str = Field(max_length=100, description="Employee first name")
    last_name: str = Field(max_length=100, description="Employee last name")
    position: str = Field(max_length=100, description="Job position")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('first_name', 'last_name', 'position')
    def strip_fields(cls, v):
        """Remove extra whitespace"""
        return v.strip() if v else v
    
    def get_full_name(self) -> str:
        """Get formatted full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_search_key(self) -> str:
        """Get search key for employee selection"""
        return f"{self.get_full_name()}#employee"
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format"""
        return {
            'PK': f'E#{self.id}',
            'SK': f'E#{self.id}',
            'Type': 'EMPLOYEE',
            'Id': self.id,
            'FN': self.first_name,
            'LN': self.last_name,
            'Pos': self.position,
            'Created': self.created_at.isoformat() if self.created_at else None,
            'Updated': self.updated_at.isoformat() if self.updated_at else None,
            # GSI1 for employee search
            'GSI1PK': 'SEARCH',
            'GSI1SK': self.get_search_key()
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Employee':
        """Create Employee from DynamoDB item"""
        return cls(
            id=item['Id'],
            first_name=item['FN'],
            last_name=item['LN'],
            position=item['Pos'],
            created_at=datetime.fromisoformat(item['Created'].replace('Z', '+00:00')) if item.get('Created') else None,
            updated_at=datetime.fromisoformat(item['Updated'].replace('Z', '+00:00')) if item.get('Updated') else None
        )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z'
        }
        allow_population_by_field_name = True

class EmployeeSearchResult(BaseModel):
    """Optimized model for employee selection"""
    
    id: str
    full_name: str
    position: str
    
    class Config:
        json_encoders = {
            str: lambda v: v.strip() if v else None
        }