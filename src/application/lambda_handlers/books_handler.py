"""
Books Lambda Handler
Handles book CRUD operations
"""
import json
import os
from typing import Dict, Any
from infrastructure.dynamodb.book_repository_impl import DynamoBookRepository
from domain.entities.book import Book


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle book operations"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Initialize repository
        table_name = os.environ['DYNAMODB_TABLE']
        book_repo = DynamoBookRepository(table_name)
        
        http_method = event['httpMethod']
        path_params = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        
        if http_method == 'GET':
            if 'book_id' in path_params:
                # Get single book
                book_id = path_params['book_id']
                book = book_repo.get_by_id(book_id)
                
                if not book:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({'error': 'Book not found'})
                    }
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(book.to_dict())
                }
            else:
                # List books with pagination
                limit = int(query_params.get('limit', 20))
                last_key = query_params.get('last_key')
                
                books, next_key = book_repo.list_books(limit, last_key)
                
                response_data = {
                    'books': [book.to_dict() for book in books],
                    'next_key': next_key
                }
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(response_data)
                }
        
        elif http_method == 'POST':
            # Create new book
            body = json.loads(event['body'])
            
            # Validate required fields
            required_fields = ['title', 'author', 'isbn']
            for field in required_fields:
                if field not in body:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({'error': f'Missing required field: {field}'})
                    }
            
            # Create book entity
            book = Book(
                book_id=None,  # Will be generated
                title=body['title'],
                author=body['author'],
                isbn=body['isbn'],
                publisher=body.get('publisher', ''),
                publication_year=body.get('publication_year'),
                genre=body.get('genre', '')
            )
            
            # Save book
            saved_book = book_repo.save(book)
            
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps(saved_book.to_dict())
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    except Exception as e:
        print(f"Error in books_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }