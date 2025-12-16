import os
from typing import List, Optional
from datetime import datetime, date
import boto3
from boto3.dynamodb.conditions import Key, Attr

from domain.entities.loan import Loan, LoanStatus
from domain.repositories.loan_repository import LoanRepository


class DynamoLoanRepository(LoanRepository):
    def __init__(self, table_name: str = None, dynamodb=None):
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE', 'lms-table')
        self.dynamodb = dynamodb or boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    async def create_loan(self, loan: Loan) -> Loan:
        item = {
            'pk': f'LOAN#{loan.loan_id}',
            'sk': 'METADATA',
            'gsi1pk': f'MEMBER#{loan.member_id}',
            'gsi1sk': f'LOAN#{loan.loan_date.isoformat()}',
            'entity_type': 'loan',
            'loan_id': loan.loan_id,
            'book_copy_id': loan.book_copy_id,
            'member_id': loan.member_id,
            'employee_id': loan.employee_id,
            'loan_date': loan.loan_date.isoformat(),
            'due_date': loan.due_date.isoformat(),
            'actual_return_date': loan.actual_return_date.isoformat() if loan.actual_return_date else None,
            'status': loan.status.value,
            'created_at': loan.created_at.isoformat() if loan.created_at else None,
            'updated_at': loan.updated_at.isoformat() if loan.updated_at else None
        }
        
        item = {k: v for k, v in item.items() if v is not None}
        self.table.put_item(Item=item)
        return loan

    async def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        response = self.table.get_item(
            Key={'pk': f'LOAN#{loan_id}', 'sk': 'METADATA'}
        )
        
        if 'Item' not in response:
            return None
            
        return self._item_to_loan(response['Item'])

    async def list_loans(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[Loan], Optional[str]]:
        kwargs = {
            'FilterExpression': Attr('entity_type').eq('loan'),
            'Limit': limit
        }
        
        if last_key:
            kwargs['ExclusiveStartKey'] = {'pk': last_key, 'sk': 'METADATA'}
        
        response = self.table.scan(**kwargs)
        loans = [self._item_to_loan(item) for item in response.get('Items', [])]
        
        next_key = None
        if 'LastEvaluatedKey' in response:
            next_key = response['LastEvaluatedKey']['pk']
        
        return loans, next_key

    async def get_loans_by_member_id(self, member_id: str) -> List[Loan]:
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('gsi1pk').eq(f'MEMBER#{member_id}') & Key('gsi1sk').begins_with('LOAN#')
        )
        
        return [self._item_to_loan(item) for item in response.get('Items', [])]

    async def get_active_loans_by_book_copy_id(self, book_copy_id: str) -> List[Loan]:
        response = self.table.scan(
            FilterExpression=Attr('book_copy_id').eq(book_copy_id) & Attr('status').eq('Prestado')
        )
        
        return [self._item_to_loan(item) for item in response.get('Items', [])]

    async def update_loan(self, loan: Loan) -> Loan:
        return await self.create_loan(loan)

    async def get_overdue_loans(self) -> List[Loan]:
        today = date.today().isoformat()
        response = self.table.scan(
            FilterExpression=Attr('entity_type').eq('loan') & 
                           Attr('status').eq('Prestado') & 
                           Attr('due_date').lt(today)
        )
        
        return [self._item_to_loan(item) for item in response.get('Items', [])]

    def _item_to_loan(self, item: dict) -> Loan:
        return Loan(
            loan_id=item['loan_id'],
            book_copy_id=item['book_copy_id'],
            member_id=item['member_id'],
            employee_id=item.get('employee_id'),
            loan_date=date.fromisoformat(item['loan_date']),
            due_date=date.fromisoformat(item['due_date']),
            actual_return_date=date.fromisoformat(item['actual_return_date']) if item.get('actual_return_date') else None,
            status=LoanStatus(item['status']),
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None
        )