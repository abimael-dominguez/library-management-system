import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
import uuid

from src.domain.entities.book import Book, BookCopy, BookStatus
from src.application.use_cases.book_service import BookService
from src.application.dto.book_dto import CreateBookRequest


class MockBookRepository:
    def __init__(self):
        self.books = {}
        
    async def create_book(self, book: Book) -> Book:
        self.books[book.book_id] = book
        return book
        
    async def get_book_by_id(self, book_id: str):
        return self.books.get(book_id)
        
    async def search_books(self, query: str, limit: int = 10):
        results = []
        for book in self.books.values():
            if query.lower() in book.title.lower() or query.lower() in book.author.lower():
                results.append(book)
                if len(results) >= limit:
                    break
        return results
        
    async def autocomplete_books(self, query: str, limit: int = 5):
        results = []
        for book in self.books.values():
            if query.lower() in book.title.lower():
                results.append({
                    'id': book.book_id,
                    'title': book.title,
                    'author': book.author
                })
                if len(results) >= limit:
                    break
        return results
        
    async def list_books(self, limit: int = 50, last_key=None):
        books = list(self.books.values())[:limit]
        return books, None


class MockBookCopyRepository:
    def __init__(self):
        self.copies = {}
        
    async def create_book_copy(self, book_copy: BookCopy) -> BookCopy:
        self.copies[book_copy.book_copy_id] = book_copy
        return book_copy
        
    async def get_book_copy_by_id(self, book_copy_id: str):
        return self.copies.get(book_copy_id)


@pytest.fixture
def book_service():
    book_repo = MockBookRepository()
    book_copy_repo = MockBookCopyRepository()
    return BookService(book_repo, book_copy_repo), book_repo, book_copy_repo


@pytest.mark.asyncio
async def test_create_book(book_service):
    service, book_repo, book_copy_repo = book_service
    
    request = CreateBookRequest(
        title="Test Book",
        author="Test Author",
        isbn="978-0123456789",
        total_copies=2
    )
    
    result = await service.create_book(request)
    
    assert result.title == "Test Book"
    assert result.author == "Test Author"
    assert result.isbn == "978-0123456789"
    assert result.total_copies == 2
    
    # Check that book was stored
    stored_book = await book_repo.get_book_by_id(result.book_id)
    assert stored_book is not None
    assert stored_book.title == "Test Book"
    
    # Check that copies were created
    copy_1 = await book_copy_repo.get_book_copy_by_id(f"{result.book_id}-001")
    copy_2 = await book_copy_repo.get_book_copy_by_id(f"{result.book_id}-002")
    assert copy_1 is not None
    assert copy_2 is not None
    assert copy_1.status == BookStatus.AVAILABLE
    assert copy_2.status == BookStatus.AVAILABLE


@pytest.mark.asyncio
async def test_search_books(book_service):
    service, book_repo, book_copy_repo = book_service
    
    # Create test books
    book1 = Book(
        book_id="1",
        title="Python Programming",
        author="John Doe",
        created_at=datetime.utcnow()
    )
    book2 = Book(
        book_id="2", 
        title="Java Development",
        author="Jane Smith",
        created_at=datetime.utcnow()
    )
    
    await book_repo.create_book(book1)
    await book_repo.create_book(book2)
    
    # Search for Python
    results = await service.search_books("Python")
    assert len(results) == 1
    assert results[0].title == "Python Programming"
    
    # Search for programming (case insensitive)
    results = await service.search_books("programming")
    assert len(results) == 1
    assert results[0].title == "Python Programming"


@pytest.mark.asyncio
async def test_autocomplete_books(book_service):
    service, book_repo, book_copy_repo = book_service
    
    # Create test book
    book = Book(
        book_id="1",
        title="Python Programming Guide",
        author="John Doe",
        created_at=datetime.utcnow()
    )
    await book_repo.create_book(book)
    
    # Test autocomplete
    results = await service.autocomplete_books("Python")
    assert len(results) == 1
    assert results[0]['title'] == "Python Programming Guide"
    assert results[0]['author'] == "John Doe"


@pytest.mark.asyncio
async def test_get_book(book_service):
    service, book_repo, book_copy_repo = book_service
    
    # Create test book
    book = Book(
        book_id="test-id",
        title="Test Book",
        author="Test Author",
        created_at=datetime.utcnow()
    )
    await book_repo.create_book(book)
    
    # Get book
    result = await service.get_book("test-id")
    assert result is not None
    assert result.title == "Test Book"
    assert result.author == "Test Author"
    
    # Get non-existent book
    result = await service.get_book("non-existent")
    assert result is None