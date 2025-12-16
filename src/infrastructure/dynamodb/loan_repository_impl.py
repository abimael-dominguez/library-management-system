"""
DynamoDB Loan Repository Implementation - Optimized for Status Queries
"""

import boto3
from typing import List, Optional
from datetime import datetime, date
from botocore.exceptions import ClientError

from ...domain.repositories.loan_repository import LoanRepository
from ...domain.entities.loan import Loan, LoanSummary, LoanStatus
from ...shared.exceptions import LoanNotFoundError, ValidationError

class DynamoLoanRepository(LoanRepository):
    """DynamoDB implementation of LoanRepository with status optimization"""
    
    def __init__(self, table_name: str = 'lms-main', region: str = 'us-east-1'):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    async def create_loan(self, loan: Loan) -> Loan:
        """Create a new loan"""
        loan.created_at = datetime.utcnow()
        loan.updated_at = datetime.utcnow()
        
        try:
            self.table.put_item(
                Item=loan.to_dynamodb_item(),
                ConditionExpression='attribute_not_exists(PK)'
            )
            return loan
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValidationError(f"Loan with ID {loan.id} already exists")
            raise
    
    async def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        """Get loan by ID"""
        try:
            response = self.table.get_item(
                Key={'PK': f'L#{loan_id}', 'SK': f'L#{loan_id}'}
            )
            
            if 'Item' in response:
                return Loan.from_dynamodb_item(response['Item'])
            return None
            
        except ClientError as e:
            print(f"Error getting loan {loan_id}: {e}")
            return None
    
    async def update_loan(self, loan: Loan) -> Loan:
        """Update existing loan"""
        loan.updated_at = datetime.utcnow()
        
        try:
            self.table.put_item(
                Item=loan.to_dynamodb_item(),
                ConditionExpression='attribute_exists(PK)'
            )
            return loan
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise LoanNotFoundError(f"Loan with ID {loan.id} not found")
            raise
    
    async def return_book(self, loan_id: str, return_date: Optional[date] = None) -> Loan:
        """Mark book as returned"""
        loan = await self.get_loan_by_id(loan_id)
        if not loan:
            raise LoanNotFoundError(f"Loan {loan_id} not found")
        
        loan.return_book(return_date)
        return await self.update_loan(loan)
    
    async def extend_loan(self, loan_id: str, weeks: int = 1) -> Loan:
        """Extend loan due date"""
        loan = await self.get_loan_by_id(loan_id)
        if not loan:
            raise LoanNotFoundError(f"Loan {loan_id} not found")
        
        loan.extend_due_date(weeks)
        return await self.update_loan(loan)
    
    async def get_loans_by_member(self, member_id: str, status: Optional[LoanStatus] = None) -> List[LoanSummary]:
        """Get loans for a specific member"""
        try:
            # Use scan with filter since we don't have member-specific GSI
            filter_expression = '#type = :type AND MemberId = :member_id'
            expression_values = {
                ':type': 'LOAN',
                ':member_id': member_id
            }
            
            if status:
                filter_expression += ' AND #status = :status'
                expression_values[':status'] = status.value
            
            response = self.table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeNames={
                    '#type': 'Type',
                    '#status': 'Status'
                },
                ExpressionAttributeValues=expression_values
            )
            
            loans = []
            for item in response['Items']:
                loan = Loan.from_dynamodb_item(item)
                loans.append(LoanSummary(
                    id=loan.id,
                    book_title=loan.book_title,
                    member_name=loan.member_name,
                    loan_date=loan.loan_date,
                    due_date=loan.due_date,
                    return_date=loan.return_date,
                    status=loan.status,
                    days_overdue=loan.days_overdue()
                ))
            
            return loans
            
        except ClientError as e:
            print(f"Error getting loans for member {member_id}: {e}")
            return []
    
    async def get_active_loans(self, limit: int = 50) -> List[LoanSummary]:
        """Get all active loans using GSI1"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :status AND begins_with(GSI1SK, :prefix)',
                ExpressionAttributeValues={
                    ':status': 'STATUS',
                    ':prefix': 'in_progress'
                },
                Limit=limit
            )
            
            loans = []
            for item in response['Items']:
                loan = Loan.from_dynamodb_item(item)
                loans.append(LoanSummary(
                    id=loan.id,
                    book_title=loan.book_title,
                    member_name=loan.member_name,
                    loan_date=loan.loan_date,
                    due_date=loan.due_date,
                    return_date=loan.return_date,
                    status=loan.status,
                    days_overdue=loan.days_overdue()
                ))
            
            return loans
            
        except ClientError as e:
            print(f"Error getting active loans: {e}")
            return []
    
    async def get_overdue_loans(self, limit: int = 50) -> List[LoanSummary]:
        """Get overdue loans using GSI1 with date filtering"""
        try:
            today = date.today().isoformat()
            
            # Query for in_progress loans and filter by due date
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :status AND GSI1SK < :today',
                ExpressionAttributeValues={
                    ':status': 'STATUS',
                    ':today': f'in_progress#{today}'
                },
                Limit=limit
            )
            
            loans = []
            for item in response['Items']:
                loan = Loan.from_dynamodb_item(item)
                # Double-check that it's actually overdue
                if loan.is_overdue():
                    loans.append(LoanSummary(
                        id=loan.id,
                        book_title=loan.book_title,
                        member_name=loan.member_name,
                        loan_date=loan.loan_date,
                        due_date=loan.due_date,
                        return_date=loan.return_date,
                        status=loan.status,
                        days_overdue=loan.days_overdue()
                    ))
            
            return loans
            
        except ClientError as e:
            print(f"Error getting overdue loans: {e}")
            return []
    
    async def get_loans_by_book(self, book_id: str) -> List[LoanSummary]:
        """Get loan history for a book"""
        try:
            response = self.table.scan(
                FilterExpression='#type = :type AND BookId = :book_id',
                ExpressionAttributeNames={'#type': 'Type'},
                ExpressionAttributeValues={
                    ':type': 'LOAN',
                    ':book_id': book_id
                }
            )
            
            loans = []
            for item in response['Items']:
                loan = Loan.from_dynamodb_item(item)
                loans.append(LoanSummary(
                    id=loan.id,
                    book_title=loan.book_title,
                    member_name=loan.member_name,
                    loan_date=loan.loan_date,
                    due_date=loan.due_date,
                    return_date=loan.return_date,
                    status=loan.status,
                    days_overdue=loan.days_overdue()
                ))
            
            # Sort by loan date (most recent first)
            loans.sort(key=lambda x: x.loan_date, reverse=True)
            return loans
            
        except ClientError as e:
            print(f"Error getting loans for book {book_id}: {e}")
            return []
    
    async def get_loans_by_copy(self, copy_id: str) -> List[LoanSummary]:
        """Get loan history for a specific copy"""
        try:
            response = self.table.scan(
                FilterExpression='#type = :type AND CopyId = :copy_id',
                ExpressionAttributeNames={'#type': 'Type'},
                ExpressionAttributeValues={
                    ':type': 'LOAN',
                    ':copy_id': copy_id
                }
            )
            
            loans = []
            for item in response['Items']:
                loan = Loan.from_dynamodb_item(item)
                loans.append(LoanSummary(
                    id=loan.id,
                    book_title=loan.book_title,
                    member_name=loan.member_name,
                    loan_date=loan.loan_date,
                    due_date=loan.due_date,
                    return_date=loan.return_date,
                    status=loan.status,
                    days_overdue=loan.days_overdue()
                ))
            
            # Sort by loan date (most recent first)
            loans.sort(key=lambda x: x.loan_date, reverse=True)
            return loans
            
        except ClientError as e:
            print(f"Error getting loans for copy {copy_id}: {e}")
            return []
    
    async def get_loans_by_date_range(self, start_date: date, end_date: date) -> List[LoanSummary]:
        """Get loans within date range"""
        try:
            response = self.table.scan(
                FilterExpression='#type = :type AND LoanDate BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={'#type': 'Type'},
                ExpressionAttributeValues={
                    ':type': 'LOAN',
                    ':start_date': start_date.isoformat(),
                    ':end_date': end_date.isoformat()
                }
            )
            
            loans = []
            for item in response['Items']:
                loan = Loan.from_dynamodb_item(item)
                loans.append(LoanSummary(
                    id=loan.id,
                    book_title=loan.book_title,
                    member_name=loan.member_name,
                    loan_date=loan.loan_date,
                    due_date=loan.due_date,
                    return_date=loan.return_date,
                    status=loan.status,
                    days_overdue=loan.days_overdue()
                ))
            
            # Sort by loan date
            loans.sort(key=lambda x: x.loan_date, reverse=True)
            return loans
            
        except ClientError as e:
            print(f"Error getting loans by date range: {e}")
            return []
    
    async def get_loan_statistics(self) -> dict:
        """Get loan statistics for dashboard"""
        try:
            # Get all loans for statistics
            response = self.table.scan(
                FilterExpression='#type = :type',
                ExpressionAttributeNames={'#type': 'Type'},
                ExpressionAttributeValues={':type': 'LOAN'}
            )
            
            loans = [Loan.from_dynamodb_item(item) for item in response['Items']]
            
            # Calculate statistics
            total_loans = len(loans)
            active_loans = len([l for l in loans if l.status == LoanStatus.IN_PROGRESS])
            returned_loans = len([l for l in loans if l.status == LoanStatus.RETURNED])
            overdue_loans = len([l for l in loans if l.is_overdue()])
            
            # Calculate average loan duration for returned books
            returned_with_dates = [l for l in loans if l.status == LoanStatus.RETURNED and l.return_date]
            avg_loan_days = 0
            if returned_with_dates:
                total_days = sum([(l.return_date - l.loan_date).days for l in returned_with_dates])
                avg_loan_days = round(total_days / len(returned_with_dates), 1)
            
            return {
                'total_loans': total_loans,
                'active_loans': active_loans,
                'returned_loans': returned_loans,
                'overdue_loans': overdue_loans,
                'overdue_percentage': round((overdue_loans / active_loans * 100) if active_loans > 0 else 0, 1),
                'return_rate': round((returned_loans / total_loans * 100) if total_loans > 0 else 0, 1),
                'average_loan_days': avg_loan_days,
                'generated_at': datetime.utcnow().isoformat() + 'Z'
            }
            
        except ClientError as e:
            print(f"Error getting loan statistics: {e}")
            return {
                'total_loans': 0,
                'active_loans': 0,
                'returned_loans': 0,
                'overdue_loans': 0,
                'overdue_percentage': 0,
                'return_rate': 0,
                'average_loan_days': 0,
                'generated_at': datetime.utcnow().isoformat() + 'Z'
            }