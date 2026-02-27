import pytest
import json
import os
from unittest.mock import patch, AsyncMock, MagicMock

from application.lambda_handlers.books_handler import async_handler as books_handler
from application.lambda_handlers.loans_handler import async_handler as loans_handler


@pytest.mark.asyncio
async def test_books_handler_list_books():
    event = {
        'httpMethod': 'GET',
        'path': '/books',
        'queryStringParameters': {'limit': '10'}
    }
    
    with patch('application.lambda_handlers.books_handler.DynamoBookRepository') as mock_book_repo, \
         patch('application.lambda_handlers.books_handler.DynamoBookCopyRepository') as mock_copy_repo:
        
        # Mock the service response
        mock_service = AsyncMock()
        mock_service.list_books.return_value = ([], None)
        
        with patch('application.lambda_handlers.books_handler.BookService', return_value=mock_service):
            response = await books_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'books' in body
        assert 'nextKey' in body


@pytest.mark.asyncio
async def test_books_handler_create_book():
    event = {
        'httpMethod': 'POST',
        'path': '/books',
        'body': json.dumps({
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '978-0123456789'
        })
    }
    
    # Mock environment variables
    with patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'us-east-1'}):
        with patch('application.lambda_handlers.books_handler.DynamoBookRepository') as mock_book_repo, \
             patch('application.lambda_handlers.books_handler.DynamoBookCopyRepository') as mock_copy_repo:
            
            # Mock the service response
            mock_service = AsyncMock()
            mock_book_response = MagicMock()
            mock_book_response.dict.return_value = {
                'book_id': 'test-id',
                'title': 'Test Book',
                'author': 'Test Author'
            }
            mock_service.create_book.return_value = mock_book_response
            
            with patch('application.lambda_handlers.books_handler.BookService', return_value=mock_service):
                response = await books_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['title'] == 'Test Book'


@pytest.mark.asyncio
async def test_books_handler_search():
    event = {
        'httpMethod': 'GET',
        'path': '/search',
        'queryStringParameters': {'q': 'python', 'limit': '5'}
    }
    
    with patch('application.lambda_handlers.books_handler.DynamoBookRepository') as mock_book_repo, \
         patch('application.lambda_handlers.books_handler.DynamoBookCopyRepository') as mock_copy_repo:
        
        # Mock the service response
        mock_service = AsyncMock()
        mock_book = MagicMock()
        mock_book.dict.return_value = {'title': 'Python Programming', 'author': 'John Doe'}
        mock_service.search_books.return_value = [mock_book]
        
        with patch('application.lambda_handlers.books_handler.BookService', return_value=mock_service):
            response = await books_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'books' in body
        assert len(body['books']) == 1


@pytest.mark.asyncio
async def test_books_handler_autocomplete():
    event = {
        'httpMethod': 'GET',
        'path': '/autocomplete',
        'queryStringParameters': {'q': 'py', 'type': 'book', 'limit': '3'}
    }
    
    with patch('application.lambda_handlers.books_handler.DynamoBookRepository') as mock_book_repo, \
         patch('application.lambda_handlers.books_handler.DynamoBookCopyRepository') as mock_copy_repo:
        
        # Mock the service response
        mock_service = AsyncMock()
        mock_service.autocomplete_books.return_value = [
            {'id': '1', 'title': 'Python Programming', 'author': 'John Doe'}
        ]
        
        with patch('application.lambda_handlers.books_handler.BookService', return_value=mock_service):
            response = await books_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'results' in body
        assert len(body['results']) == 1


@pytest.mark.asyncio
async def test_loans_handler_create_loan():
    event = {
        'httpMethod': 'POST',
        'path': '/loans',
        'body': json.dumps({
            'book_copy_id': 'book-1-001',
            'member_id': 'member-1',
            'employee_id': 'employee-1',
            'loan_date': '2024-01-01',
            'due_date': '2024-01-22'
        })
    }
    
    with patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'us-east-1'}):
        with patch('application.lambda_handlers.loans_handler.DynamoLoanRepository') as mock_loan_repo, \
             patch('application.lambda_handlers.loans_handler.DynamoBookCopyRepository') as mock_copy_repo:
            
            # Mock the service response
            mock_service = AsyncMock()
            mock_loan_response = MagicMock()
            mock_loan_response.dict.return_value = {
                'loan_id': 'loan-1',
                'book_copy_id': 'book-1-001',
                'member_id': 'member-1',
                'status': 'in_progress'
            }
            mock_service.create_loan.return_value = mock_loan_response
            
            with patch('application.lambda_handlers.loans_handler.LoanService', return_value=mock_service):
                response = await loans_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['loan_id'] == 'loan-1'
            assert body['status'] == 'in_progress'


@pytest.mark.asyncio
async def test_loans_handler_return_loan():
    event = {
        'httpMethod': 'PUT',
        'path': '/loans/loan-1/return',
        'body': json.dumps({})
    }
    
    with patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'us-east-1'}):
        with patch('application.lambda_handlers.loans_handler.DynamoLoanRepository') as mock_loan_repo, \
             patch('application.lambda_handlers.loans_handler.DynamoBookCopyRepository') as mock_copy_repo:
            
            # Mock the service response
            mock_service = AsyncMock()
            mock_loan_response = MagicMock()
            mock_loan_response.dict.return_value = {
                'loan_id': 'loan-1',
                'status': 'returned'
            }
            mock_service.return_loan.return_value = mock_loan_response
            
            with patch('application.lambda_handlers.loans_handler.LoanService', return_value=mock_service):
                response = await loans_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['status'] == 'returned'


@pytest.mark.asyncio
async def test_cors_options_request():
    event = {
        'httpMethod': 'OPTIONS',
        'path': '/books'
    }
    
    with patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'us-east-1'}):
        response = await books_handler(event, {})
    
    assert response['statusCode'] == 200
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
