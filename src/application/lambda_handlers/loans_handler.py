"""
Loans Lambda Handler - Fast Loan/Return Workflow API
"""

import json
import asyncio
from typing import Dict, Any
from datetime import date, datetime
from ...infrastructure.dynamodb.book_repository_impl import DynamoBookRepository, DynamoBookCopyRepository
from ...infrastructure.dynamodb.member_repository_impl import DynamoMemberRepository, DynamoEmployeeRepository
from ...infrastructure.dynamodb.loan_repository_impl import DynamoLoanRepository
from ..use_cases.loan_service import LoanService

# Initialize dependencies (reused across Lambda invocations)
book_repository = DynamoBookRepository()
book_copy_repository = DynamoBookCopyRepository()
member_repository = DynamoMemberRepository()
employee_repository = DynamoEmployeeRepository()
loan_repository = DynamoLoanRepository()

loan_service = LoanService(
    loan_repository=loan_repository,
    book_repository=book_repository,
    book_copy_repository=book_copy_repository,
    member_repository=member_repository,
    employee_repository=employee_repository
)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for loan operations
    
    Routes:
    - POST /loans - Create new loan (Préstamo)
    - PUT /loans/{id}/return - Return book (Devolución)
    - PUT /loans/{id}/extend - Extend loan
    - GET /loans/overdue - Get overdue loans
    - GET /loans/active - Get active loans
    - GET /loans/member/{member_id} - Get member loans
    - GET /loans/stats - Get loan statistics
    - POST /loans/bulk-return - Return multiple books
    """
    
    try:
        # Extract request info
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body', '{}')
        
        # CORS headers
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS'
        }
        
        # Handle OPTIONS for CORS
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Route to appropriate handler
        if http_method == 'POST':
            if path.endswith('/bulk-return'):
                return asyncio.run(handle_bulk_return(body, headers))
            else:
                return asyncio.run(handle_create_loan(body, headers))
        
        elif http_method == 'PUT':
            loan_id = path_parameters.get('id')
            if not loan_id:
                return error_response("Missing loan ID", 400, headers)
            
            if path.endswith('/return'):
                return asyncio.run(handle_return_book(loan_id, body, headers))
            elif path.endswith('/extend'):
                return asyncio.run(handle_extend_loan(loan_id, body, headers))
        
        elif http_method == 'GET':
            if path.endswith('/overdue'):
                return asyncio.run(handle_get_overdue_loans(query_params, headers))
            elif path.endswith('/active'):
                return asyncio.run(handle_get_active_loans(query_params, headers))
            elif path.endswith('/stats'):
                return asyncio.run(handle_get_statistics(headers))
            elif '/member/' in path:
                member_id = path_parameters.get('member_id')
                return asyncio.run(handle_get_member_loans(member_id, query_params, headers))
        
        return error_response("Route not found", 404, headers)
        
    except Exception as e:
        print(f"Lambda error: {e}")
        return error_response(f"Internal server error: {str(e)}", 500, headers)

async def handle_create_loan(body: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle loan creation (Préstamo)"""
    try:
        data = json.loads(body)
        
        # Validate required fields
        book_id = data.get('book_id')
        member_id = data.get('member_id')
        
        if not book_id or not member_id:
            return error_response("Missing required fields: book_id, member_id", 400, headers)
        
        # Optional fields
        employee_id = data.get('employee_id')
        loan_weeks = data.get('loan_weeks', 2)
        
        # Create loan
        loan = await loan_service.create_loan(
            book_id=book_id,
            member_id=member_id,
            employee_id=employee_id,
            loan_weeks=loan_weeks
        )
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'loan': loan.dict(),
                'message': f'Loan created successfully for "{loan.book_title}"'
            })
        }
        
    except Exception as e:
        return error_response(str(e), 400, headers)

async def handle_return_book(loan_id: str, body: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle book return (Devolución)"""
    try:
        data = json.loads(body) if body else {}
        return_date_str = data.get('return_date')
        
        return_date = None
        if return_date_str:
            return_date = date.fromisoformat(return_date_str)
        
        # Return book
        loan = await loan_service.return_book(loan_id, return_date)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'loan': loan.dict(),
                'message': f'Book "{loan.book_title}" returned successfully'
            })
        }
        
    except Exception as e:
        return error_response(str(e), 400, headers)

async def handle_extend_loan(loan_id: str, body: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle loan extension"""
    try:
        data = json.loads(body) if body else {}
        weeks = data.get('weeks', 1)
        
        loan = await loan_service.extend_loan(loan_id, weeks)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'loan': loan.dict(),
                'message': f'Loan extended by {weeks} week(s)'
            })
        }
        
    except Exception as e:
        return error_response(str(e), 400, headers)

async def handle_get_overdue_loans(query_params: Dict[str, str], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle getting overdue loans"""
    try:
        limit = min(int(query_params.get('limit', 50)), 100)
        loans = await loan_service.get_overdue_loans(limit)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'loans': [loan.dict() for loan in loans],
                'total': len(loans),
                'limit': limit
            })
        }
        
    except Exception as e:
        return error_response(str(e), 500, headers)

async def handle_get_active_loans(query_params: Dict[str, str], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle getting active loans"""
    try:
        limit = min(int(query_params.get('limit', 50)), 100)
        loans = await loan_service.get_active_loans(limit)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'loans': [loan.dict() for loan in loans],
                'total': len(loans),
                'limit': limit
            })
        }
        
    except Exception as e:
        return error_response(str(e), 500, headers)

async def handle_get_member_loans(member_id: str, query_params: Dict[str, str], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle getting loans for a specific member"""
    try:
        if not member_id:
            return error_response("Missing member_id", 400, headers)
        
        status_str = query_params.get('status')
        status = None
        if status_str:
            from ...domain.entities.loan import LoanStatus
            status = LoanStatus(status_str)
        
        loans = await loan_service.get_member_loans(member_id, status)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'loans': [loan.dict() for loan in loans],
                'member_id': member_id,
                'status_filter': status_str,
                'total': len(loans)
            })
        }
        
    except Exception as e:
        return error_response(str(e), 400, headers)

async def handle_get_statistics(headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle getting loan statistics"""
    try:
        stats = await loan_service.get_loan_statistics()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'statistics': stats,
                'generated_at': datetime.utcnow().isoformat() + 'Z'
            })
        }
        
    except Exception as e:
        return error_response(str(e), 500, headers)

async def handle_bulk_return(body: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle bulk book returns"""
    try:
        data = json.loads(body)
        loan_ids = data.get('loan_ids', [])
        
        if not loan_ids:
            return error_response("Missing loan_ids array", 400, headers)
        
        results = await loan_service.bulk_return_books(loan_ids)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        return error_response(str(e), 400, headers)

def error_response(message: str, status_code: int, headers: Dict[str, str]) -> Dict[str, Any]:
    """Helper function to create error responses"""
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    }