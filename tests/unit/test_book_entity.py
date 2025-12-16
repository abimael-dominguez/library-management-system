"""
Unit tests for Book entity
"""
import pytest
from datetime import datetime
from src.domain.entities.book import Book


class TestBookEntity:
    
    def test_book_creation(self):
        """Test basic book creation"""
        book = Book(
            book_id="book_123",
            title="Test Book",
            author="Test Author",
            isbn="978-0123456789",
            publisher="Test Publisher",
            publication_year=2023,
            genre="Fiction"
        )
        
        assert book.book_id == "book_123"
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.isbn == "978-0123456789"
        assert book.status == "available"
    
    def test_book_to_dict(self):
        """Test book serialization to dictionary"""
        book = Book(
            book_id="book_123",
            title="Test Book",
            author="Test Author",
            isbn="978-0123456789"
        )
        
        book_dict = book.to_dict()
        
        assert book_dict["book_id"] == "book_123"
        assert book_dict["title"] == "Test Book"
        assert book_dict["author"] == "Test Author"
        assert book_dict["isbn"] == "978-0123456789"
        assert book_dict["status"] == "available"
    
    def test_book_to_dynamodb_item(self):
        """Test book serialization to DynamoDB format"""
        book = Book(
            book_id="book_123",
            title="Test Book",
            author="Test Author",
            isbn="978-0123456789"
        )
        
        item = book.to_dynamodb_item()
        
        assert item["pk"] == "BOOK#book_123"
        assert item["sk"] == "METADATA"
        assert item["gsi1pk"] == "SEARCH#book"
        assert "Test Book" in item["gsi1sk"]
        assert item["title"] == "Test Book"
        assert item["author"] == "Test Author"
    
    def test_book_from_dynamodb_item(self):
        """Test book deserialization from DynamoDB format"""
        item = {
            "pk": "BOOK#book_123",
            "sk": "METADATA",
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-0123456789",
            "publisher": "Test Publisher",
            "publication_year": 2023,
            "genre": "Fiction",
            "status": "available",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        book = Book.from_dynamodb_item(item)
        
        assert book.book_id == "book_123"
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.isbn == "978-0123456789"
        assert book.status == "available"
    
    def test_book_search_text_generation(self):
        """Test search text generation for GSI"""
        book = Book(
            book_id="book_123",
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="978-0123456789",
            genre="Classic Literature"
        )
        
        search_text = book._generate_search_text()
        
        # Should contain title, author, ISBN, and genre in lowercase
        assert "the great gatsby" in search_text
        assert "f. scott fitzgerald" in search_text
        assert "978-0123456789" in search_text
        assert "classic literature" in search_text