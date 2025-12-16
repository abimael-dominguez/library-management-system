"""
Book Repository Interface - Abstract Contract for Data Access
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.book import Book, BookCopy, BookSearchResult

class BookRepository(ABC):
    """Abstract repository interface for book operations"""
    
    @abstractmethod
    async def create_book(self, book: Book) -> Book:
        """Create a new book"""
        pass
    
    @abstractmethod
    async def create_multiple_books(self, books: List[Book]) -> dict:
        """Create multiple books with batch optimization"""
        pass
    
    @abstractmethod
    async def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Get book by ID"""
        pass
    
    @abstractmethod
    async def get_book_with_copies(self, book_id: str) -> Optional[dict]:
        """Get book with all its copies"""
        pass
    
    @abstractmethod
    async def search_books(self, query: str, limit: int = 10) -> List[BookSearchResult]:
        """Search books for autocomplete (ultra-fast)"""
        pass
    
    @abstractmethod
    async def update_book(self, book: Book) -> Book:
        """Update existing book"""
        pass
    
    @abstractmethod
    async def update_available_copies(self, book_id: str, delta: int) -> bool:
        """Update available copies count (+1 for return, -1 for loan)"""
        pass
    
    @abstractmethod
    async def list_books(self, limit: int = 50, last_key: Optional[str] = None) -> dict:
        """List books with pagination"""
        pass

class BookCopyRepository(ABC):
    """Abstract repository interface for book copy operations"""
    
    @abstractmethod
    async def create_copy(self, copy: BookCopy) -> BookCopy:
        """Create a new book copy"""
        pass
    
    @abstractmethod
    async def get_copy_by_id(self, copy_id: str) -> Optional[BookCopy]:
        """Get copy by ID"""
        pass
    
    @abstractmethod
    async def get_copies_by_book_id(self, book_id: str) -> List[BookCopy]:
        """Get all copies for a book"""
        pass
    
    @abstractmethod
    async def get_available_copies(self, book_id: str) -> List[BookCopy]:
        """Get available copies for a book"""
        pass
    
    @abstractmethod
    async def update_copy_status(self, copy_id: str, status: str) -> bool:
        """Update copy status (available, loaned, damaged, lost)"""
        pass