import json
import asyncio
from typing import Dict, Any

from infrastructure.dynamodb.book_repository_impl import DynamoBookRepository, DynamoBookCopyRepository
from application.use_cases.book_service import BookService
from application.dto.book_dto import CreateBookRequest, SearchBooksRequest, AutocompleteRequest


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    return asyncio.run(async_handler(event, context))


async def async_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Initialize repositories and service
        book_repo = DynamoBookRepository()
        book_copy_repo = DynamoBookCopyRepository()
        book_service = BookService(book_repo, book_copy_repo)
        
        http_method = event['httpMethod']
        path = event['path']
        query_params = event.get('queryStringParameters') or {}
        
        if http_method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        # Route handling
        if path == '/books' and http_method == 'GET':
            limit = int(query_params.get('limit', 50))
            last_key = query_params.get('lastKey')
            books, next_key = await book_service.list_books(limit, last_key)
            
            response_body = {
                'books': [book.dict() for book in books],
                'nextKey': next_key
            }
            
        elif path == '/books' and http_method == 'POST':
            body = json.loads(event['body'])
            request = CreateBookRequest(**body)
            book = await book_service.create_book(request)
            response_body = book.dict()
            
        elif path.startswith('/books/') and http_method == 'GET':
            book_id = path.split('/')[-1]
            book = await book_service.get_book(book_id)
            if not book:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': 'Book not found'})
                }
            response_body = book.dict()
            
        elif path == '/search' and http_method == 'GET':
            query = query_params.get('q', '')
            limit = int(query_params.get('limit', 10))
            
            if not query:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Query parameter q is required'})
                }
            
            books = await book_service.search_books(query, limit)
            response_body = {'books': [book.dict() for book in books]}
            
        elif path == '/autocomplete' and http_method == 'GET':
            query = query_params.get('q', '')
            search_type = query_params.get('type', 'book')
            limit = int(query_params.get('limit', 5))
            
            if not query:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Query parameter q is required'})
                }
            
            if search_type == 'book':
                results = await book_service.autocomplete_books(query, limit)
                response_body = {'results': results}
            else:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid type parameter'})
                }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_body, default=str)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }