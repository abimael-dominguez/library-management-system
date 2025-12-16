"""
Unit tests for SearchService
"""
import pytest
from unittest.mock import Mock, patch
from src.application.use_cases.search_service import SearchService
from src.domain.entities.book import Book
from src.domain.entities.member import Member


class TestSearchService:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_search_repo = Mock()
        self.search_service = SearchService(self.mock_search_repo)
    
    def test_search_books_success(self):
        """Test successful book search"""
        # Mock data
        mock_books = [
            Book(
                id="book_1",
                title="Python Programming",
                author="John Doe",
                isbn="978-0123456789"
            ),
            Book(
                id="book_2", 
                title="Advanced Python",
                author="Jane Smith",
                isbn="978-0987654321"
            )
        ]
        
        self.mock_search_repo.search_books.return_value = mock_books
        
        # Execute
        results = self.search_service.search_books("python", limit=10)
        
        # Assert
        assert len(results) == 2
        assert results[0].title == "Python Programming"
        assert results[1].title == "Advanced Python"
        self.mock_search_repo.search_books.assert_called_once_with("python", 10)
    
    def test_search_members_success(self):
        """Test successful member search"""
        # Mock data
        mock_members = [
            Member(
                id="member_1",
                first_name="John",
                last_name="Doe",
                email="john@example.com"
            )
        ]
        
        self.mock_search_repo.search_members.return_value = mock_members
        
        # Execute
        results = self.search_service.search_members("john", limit=5)
        
        # Assert
        assert len(results) == 1
        assert results[0].first_name == "John"
        self.mock_search_repo.search_members.assert_called_once_with("john", 5)
    
    def test_autocomplete_books(self):
        """Test book autocomplete functionality"""
        # Mock data
        mock_books = [
            Book(
                id="book_1",
                title="Harry Potter",
                author="J.K. Rowling",
                isbn="978-0123456789"
            )
        ]
        
        self.mock_search_repo.search_books.return_value = mock_books
        
        # Execute
        results = self.search_service.autocomplete("har", "book", limit=5)
        
        # Assert
        assert len(results) == 1
        assert results[0]["title"] == "Harry Potter"
        assert results[0]["type"] == "book"
        self.mock_search_repo.search_books.assert_called_once_with("har", 5)
    
    def test_autocomplete_members(self):
        """Test member autocomplete functionality"""
        # Mock data
        mock_members = [
            Member(
                id="member_1",
                first_name="Maria",
                last_name="Garcia",
                email="maria@example.com"
            )
        ]
        
        self.mock_search_repo.search_members.return_value = mock_members
        
        # Execute
        results = self.search_service.autocomplete("mar", "member", limit=5)
        
        # Assert
        assert len(results) == 1
        assert results[0]["first_name"] == "Maria"
        assert results[0]["type"] == "member"
        self.mock_search_repo.search_members.assert_called_once_with("mar", 5)
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        results = self.search_service.search_books("", limit=10)
        
        assert results == []
        self.mock_search_repo.search_books.assert_not_called()
    
    def test_search_with_exception(self):
        """Test search handling exceptions"""
        self.mock_search_repo.search_books.side_effect = Exception("Database error")
        
        results = self.search_service.search_books("python", limit=10)
        
        assert results == []