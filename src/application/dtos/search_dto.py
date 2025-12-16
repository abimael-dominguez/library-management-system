"""
Search DTOs - Optimized for Ultra-Fast Autocomplete UX
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from enum import Enum

class SearchEntityType(str, Enum):
    """Entity types for search"""
    BOOK = "book"
    MEMBER = "member"
    EMPLOYEE = "employee"

class AutocompleteRequest(BaseModel):
    """Request model for autocomplete search"""
    
    query: str = Field(min_length=1, max_length=100, description="Search query")
    entity_type: SearchEntityType = Field(default=SearchEntityType.BOOK, description="Type of entity to search")
    limit: int = Field(default=10, ge=1, le=20, description="Maximum results to return")
    
    @validator('query')
    def clean_query(cls, v):
        """Clean and normalize search query"""
        return v.strip().lower()
    
    class Config:
        use_enum_values = True

class BookAutocompleteResult(BaseModel):
    """Optimized book result for autocomplete"""
    
    id: str
    title: str
    author: str
    available_copies: int
    total_copies: int
    isbn: Optional[str] = None
    
    @validator('title', 'author')
    def strip_text(cls, v):
        return v.strip() if v else v
    
    def is_available(self) -> bool:
        """Check if book has available copies"""
        return self.available_copies > 0

class MemberAutocompleteResult(BaseModel):
    """Optimized member result for autocomplete"""
    
    id: str
    full_name: str
    email: str
    status: str
    
    @validator('full_name')
    def strip_name(cls, v):
        return v.strip() if v else v
    
    def is_active(self) -> bool:
        """Check if member can borrow books"""
        return self.status == 'active'

class EmployeeAutocompleteResult(BaseModel):
    """Optimized employee result for selection"""
    
    id: str
    full_name: str
    position: str
    
    @validator('full_name', 'position')
    def strip_text(cls, v):
        return v.strip() if v else v

# Union type for autocomplete results
AutocompleteResultItem = Union[
    BookAutocompleteResult,
    MemberAutocompleteResult, 
    EmployeeAutocompleteResult
]

class AutocompleteResponse(BaseModel):
    """Response model for autocomplete search"""
    
    results: List[AutocompleteResultItem]
    total: int
    query: str
    entity_type: SearchEntityType
    query_time_ms: float = Field(description="Query execution time for monitoring")
    
    @validator('results')
    def limit_results(cls, v):
        """Ensure we don't return too many results"""
        return v[:20]  # Hard limit for performance
    
    class Config:
        use_enum_values = True

class SearchFilters(BaseModel):
    """Advanced search filters"""
    
    status: Optional[str] = Field(None, description="Filter by status")
    genre: Optional[str] = Field(None, description="Filter by book genre")
    available_only: bool = Field(default=False, description="Show only available books")
    
    class Config:
        extra = "forbid"  # Prevent unexpected filters

class AdvancedSearchRequest(BaseModel):
    """Advanced search with filters"""
    
    query: Optional[str] = Field(None, min_length=1, max_length=100)
    entity_type: SearchEntityType = Field(default=SearchEntityType.BOOK)
    filters: Optional[SearchFilters] = None
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0)
    
    @validator('query')
    def clean_query(cls, v):
        if v:
            return v.strip().lower()
        return v
    
    class Config:
        use_enum_values = True

class AdvancedSearchResponse(BaseModel):
    """Response for advanced search"""
    
    results: List[AutocompleteResultItem]
    total: int
    query: Optional[str]
    filters: Optional[SearchFilters]
    limit: int
    offset: int
    has_more: bool
    query_time_ms: float
    
    @validator('has_more', always=True)
    def calculate_has_more(cls, v, values):
        """Calculate if there are more results"""
        total = values.get('total', 0)
        limit = values.get('limit', 20)
        offset = values.get('offset', 0)
        return total > (offset + limit)
    
    class Config:
        use_enum_values = True