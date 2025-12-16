import json
import os
import boto3
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('DYNAMODB_TABLE', 'lms-table-dev')
        table = dynamodb.Table(table_name)
        
        http_method = event['httpMethod']
        path = event['path']
        query_params = event.get('queryStringParameters') or {}
        
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200, 
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                }, 
                'body': ''
            }
        
        # Route handling
        if path == '/books' and http_method == 'GET':
            # List books
            response = table.scan(
                FilterExpression='entity_type = :et',
                ExpressionAttributeValues={':et': 'book'},
                Limit=int(query_params.get('limit', 50))
            )
            
            books = []
            for item in response.get('Items', []):
                books.append({
                    'book_id': item.get('book_id'),
                    'title': item.get('title'),
                    'author': item.get('author'),
                    'isbn': item.get('isbn'),
                    'publisher': item.get('publisher'),
                    'publication_year': item.get('publication_year'),
                    'genre': item.get('genre'),
                    'pages': item.get('pages'),
                    'total_copies': item.get('total_copies', 1)
                })
            
            response_body = {'books': books}
            
        elif path == '/search' and http_method == 'GET':
            query = query_params.get('q', '')
            if not query:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Query parameter q is required'})
                }
            
            # Simple search using scan (not optimal but works)
            response = table.scan(
                FilterExpression='contains(title, :q) OR contains(author, :q)',
                ExpressionAttributeValues={':q': query},
                Limit=int(query_params.get('limit', 10))
            )
            
            books = []
            for item in response.get('Items', []):
                if item.get('entity_type') == 'book':
                    books.append({
                        'book_id': item.get('book_id'),
                        'title': item.get('title'),
                        'author': item.get('author')
                    })
            
            response_body = {'books': books}
            
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