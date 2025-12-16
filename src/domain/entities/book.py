"""
Book Domain Entity - Optimized for Cost and UX
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class Book(BaseModel):
    """Book entity optimized for DynamoDB storage and autocomplete UX"""
    
    id: str = Field(description="Unique book identifier")
    title: str = Field(max_length=255, description="Book title for search")
    author: str = Field(max_length=255, description="Primary author")
    isbn: Optional[str] = Field(None, max_length=17, description="ISBN number")
    publisher: Optional[str] = Field(None, max_length=255, description="Publisher name")
    publication_year: Optional[int] = Field(None, ge=1000, le=2030, description="Publication year")
    genre: Optional[str] = Field(None, max_length=100, description="Book genre")
    total_copies: int = Field(default=1, ge=1, description="Total physical copies")
    available_copies: int = Field(default=1, ge=0, description="Available copies for loan")
    pages: Optional[int] = Field(None, ge=1, description="Number of pages")
    max_loan_weeks: int = Field(default=2, ge=1, le=12, description="Maximum loan duration")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('available_copies')
    def available_must_not_exceed_total(cls, v, values):
        """Ensure available copies don't exceed total copies"""
        total = values.get('total_copies', 1)
        if v > total:
            raise ValueError('Available copies cannot exceed total copies')
        return v
    
    @validator('title', 'author')
    def strip_whitespace(cls, v):
        """Remove extra whitespace for consistent search"""
        return v.strip() if v else v
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format (cost-optimized)"""
        return {
            'PK': f'B#{self.id}',
            'SK': f'B#{self.id}',
            'Type': 'BOOK',
            'Id': self.id,
            'T': self.title,  # Shortened for cost
            'A': self.author,
            'ISBN': self.isbn,
            'Pub': self.publisher,
            'Year': self.publication_year,
            'Genre': self.genre,
            'Copies': self.total_copies,
            'Avail': self.available_copies,
            'Pages': self.pages,
            'MaxWeeks': self.max_loan_weeks,
            'Created': self.created_at.isoformat() if self.created_at else None,
            'Updated': self.updated_at.isoformat() if self.updated_at else None,
            # GSI1 for autocomplete search
            'GSI1PK': 'SEARCH',
            'GSI1SK': f'{self.title}#{self.author}'
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Book':
        """Create Book from DynamoDB item"""
        return cls(
            id=item['Id'],
            title=item['T'],
            author=item['A'],
            isbn=item.get('ISBN'),
            publisher=item.get('Pub'),
            publication_year=item.get('Year'),
            genre=item.get('Genre'),
            total_copies=item['Copies'],
            available_copies=item['Avail'],
            pages=item.get('Pages'),
            max_loan_weeks=item.get('MaxWeeks', 2),
            created_at=datetime.fromisoformat(item['Created'].replace('Z', '+00:00')) if item.get('Created') else None,
            updated_at=datetime.fromisoformat(item['Updated'].replace('Z', '+00:00')) if item.get('Updated') else None
        )
    
    def get_search_key(self) -> str:
        """Get the search key for autocomplete"""
        return f'{self.title}#{self.author}'
    
    class Config:
        # Enable fast JSON serialization
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z'
        }
        # Allow field aliases
        allow_population_by_field_name = True

class BookSearchResult(BaseModel):
    """Optimized model for autocomplete results"""
    
    id: str
    title: str
    author: str
    available_copies: int
    total_copies: int
    
    class Config:
        # Ultra-fast serialization for autocomplete
        json_encoders = {
            str: lambda v: v.strip() if v else None
        }

class BookCopy(BaseModel):
    """Book copy entity for inventory tracking"""
    
    id: str = Field(description="Unique copy identifier")
    book_id: str = Field(description="Reference to parent book")
    status: str = Field(regex='^(available|loaned|damaged|lost)$', description="Copy status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format"""
        return {
            'PK': f'B#{self.book_id}',  # Same PK as book for efficient queries
            'SK': f'C#{self.id}',
            'Type': 'COPY',
            'Id': self.id,
            'BookId': self.book_id,
            'Status': self.status,
            'Created': self.created_at.isoformat() if self.created_at else None,
            'Updated': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'BookCopy':
        """Create BookCopy from DynamoDB item"""
        return cls(
            id=item['Id'],
            book_id=item['BookId'],
            status=item['Status'],
            created_at=datetime.fromisoformat(item['Created'].replace('Z', '+00:00')) if item.get('Created') else None,
            updated_at=datetime.fromisoformat(item['Updated'].replace('Z', '+00:00')) if item.get('Updated') else None
        )
    
    def is_available(self) -> bool:
        """Check if copy is available for loan"""
        return self.status == 'available'