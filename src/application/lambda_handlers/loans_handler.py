import json
import asyncio
from typing import Dict, Any

from infrastructure.dynamodb.loan_repository_impl import DynamoLoanRepository
from infrastructure.dynamodb.book_repository_impl import DynamoBookCopyRepository
from application.use_cases.loan_service import LoanService
from application.dto.loan_dto import CreateLoanRequest, ReturnLoanRequest


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
        loan_repo = DynamoLoanRepository()
        book_copy_repo = DynamoBookCopyRepository()
        loan_service = LoanService(loan_repo, book_copy_repo)
        
        http_method = event['httpMethod']
        path = event['path']
        
        if http_method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        # Route handling
        if path == '/loans' and http_method == 'GET':
            query_params = event.get('queryStringParameters') or {}
            limit = int(query_params.get('limit', 50))
            last_key = query_params.get('lastKey')
            loans, next_key = await loan_service.list_loans(limit, last_key)
            
            response_body = {
                'loans': [loan.dict() for loan in loans],
                'nextKey': next_key
            }
            
        elif path == '/loans' and http_method == 'POST':
            body = json.loads(event['body'])
            request = CreateLoanRequest(**body)
            loan = await loan_service.create_loan(request)
            response_body = loan.dict()
            
        elif path.startswith('/loans/') and path.endswith('/return') and http_method == 'PUT':
            loan_id = path.split('/')[-2]
            body = json.loads(event.get('body', '{}'))
            request = ReturnLoanRequest(**body)
            loan = await loan_service.return_loan(loan_id, request)
            response_body = loan.dict()
            
        elif path.startswith('/loans/') and http_method == 'GET':
            loan_id = path.split('/')[-1]
            loan = await loan_service.get_loan(loan_id)
            if not loan:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': 'Loan not found'})
                }
            response_body = loan.dict()
            
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
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }