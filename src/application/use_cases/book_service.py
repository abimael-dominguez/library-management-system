from typing import List, Optional
import uuid
from datetime import datetime

from domain.entities.book import Book, BookCopy, BookStatus
from domain.repositories.book_repository import BookRepository, BookCopyRepository
from application.dto.book_dto import CreateBookRequest, BookResponse


class BookService:
    def __init__(self, book_repo: BookRepository, book_copy_repo: BookCopyRepository):
        self.book_repo = book_repo
        self.book_copy_repo = book_copy_repo

    async def create_book(self, request: CreateBookRequest) -> BookResponse:
        book_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        book = Book(
            book_id=book_id,
            title=request.title,
            author=request.author,
            isbn=request.isbn,
            publisher=request.publisher,
            publication_year=request.publication_year,
            genre=request.genre,
            pages=request.pages,
            max_loan_weeks=request.max_loan_weeks,
            total_copies=request.total_copies,
            created_at=now,
            updated_at=now
        )
        
        created_book = await self.book_repo.create_book(book)
        
        # Create book copies
        for i in range(request.total_copies):
            copy_id = f"{book_id}-{i+1:03d}"
            book_copy = BookCopy(
                book_copy_id=copy_id,
                book_id=book_id,
                status=BookStatus.AVAILABLE,
                created_at=now,
                updated_at=now
            )
            await self.book_copy_repo.create_book_copy(book_copy)
        
        return BookResponse(**created_book.__dict__)

    async def get_book(self, book_id: str) -> Optional[BookResponse]:
        book = await self.book_repo.get_book_by_id(book_id)
        if not book:
            return None
        return BookResponse(**book.__dict__)

    async def search_books(self, query: str, limit: int = 10) -> List[BookResponse]:
        books = await self.book_repo.search_books(query, limit)
        return [BookResponse(**book.__dict__) for book in books]

    async def autocomplete_books(self, query: str, limit: int = 5) -> List[dict]:
        return await self.book_repo.autocomplete_books(query, limit)

    async def list_books(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[BookResponse], Optional[str]]:
        books, next_key = await self.book_repo.list_books(limit, last_key)
        return [BookResponse(**book.__dict__) for book in books], next_key