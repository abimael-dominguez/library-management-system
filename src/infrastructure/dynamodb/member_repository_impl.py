"""
DynamoDB Member Repository Implementation
"""

import boto3
from typing import List, Optional
from datetime import datetime
from botocore.exceptions import ClientError

from ...domain.repositories.member_repository import MemberRepository, EmployeeRepository
from ...domain.entities.member import Member, Employee, MemberSearchResult, EmployeeSearchResult
from ...shared.exceptions import MemberNotFoundError, ValidationError

class DynamoMemberRepository(MemberRepository):
    """DynamoDB implementation of MemberRepository"""
    
    def __init__(self, table_name: str = 'lms-main', region: str = 'us-east-1'):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    async def create_member(self, member: Member) -> Member:
        """Create a new member"""
        member.created_at = datetime.utcnow()
        member.updated_at = datetime.utcnow()
        
        try:
            self.table.put_item(
                Item=member.to_dynamodb_item(),
                ConditionExpression='attribute_not_exists(PK)'
            )
            return member
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValidationError(f"Member with ID {member.id} already exists")
            raise
    
    async def get_member_by_id(self, member_id: str) -> Optional[Member]:
        """Get member by ID"""
        try:
            response = self.table.get_item(
                Key={'PK': f'M#{member_id}', 'SK': f'M#{member_id}'}
            )
            
            if 'Item' in response:
                return Member.from_dynamodb_item(response['Item'])
            return None
            
        except ClientError as e:
            print(f"Error getting member {member_id}: {e}")
            return None
    
    async def get_member_by_email(self, email: str) -> Optional[Member]:
        """Get member by email using GSI1"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :search AND contains(GSI1SK, :email)',
                ExpressionAttributeValues={
                    ':search': 'SEARCH',
                    ':email': email.lower()
                },
                Limit=1
            )
            
            for item in response['Items']:
                if item.get('Email', '').lower() == email.lower():
                    return Member.from_dynamodb_item(item)
            
            return None
            
        except ClientError as e:
            print(f"Error getting member by email {email}: {e}")
            return None
    
    async def search_members(self, query: str, limit: int = 10) -> List[MemberSearchResult]:
        """Search members for autocomplete"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :search AND begins_with(GSI1SK, :query)',
                ExpressionAttributeValues={
                    ':search': 'SEARCH',
                    ':query': query.strip().lower()
                },
                Limit=limit,
                ProjectionExpression='Id, FN, LN, Email, #status',
                ExpressionAttributeNames={'#status': 'Status'}
            )
            
            results = []
            for item in response['Items']:
                # Only include items that are members (have Email field)
                if item.get('Email') and '@' in item.get('Email', ''):
                    full_name = f"{item.get('FN', '')} {item.get('LN', '')}".strip()
                    results.append(MemberSearchResult(
                        id=item['Id'],
                        full_name=full_name,
                        email=item['Email'],
                        status=item.get('Status', 'active')
                    ))
            
            return results
            
        except ClientError as e:
            print(f"Error searching members: {e}")
            return []
    
    async def update_member(self, member: Member) -> Member:
        """Update existing member"""
        member.updated_at = datetime.utcnow()
        
        try:
            self.table.put_item(
                Item=member.to_dynamodb_item(),
                ConditionExpression='attribute_exists(PK)'
            )
            return member
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise MemberNotFoundError(f"Member with ID {member.id} not found")
            raise
    
    async def update_member_status(self, member_id: str, status: str) -> bool:
        """Update member status"""
        try:
            self.table.update_item(
                Key={'PK': f'M#{member_id}', 'SK': f'M#{member_id}'},
                UpdateExpression='SET #status = :status, Updated = :updated',
                ExpressionAttributeNames={'#status': 'Status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated': datetime.utcnow().isoformat() + 'Z'
                },
                ConditionExpression='attribute_exists(PK)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise
    
    async def list_members(self, limit: int = 50, last_key: Optional[str] = None) -> dict:
        """List members with pagination"""
        try:
            scan_params = {
                'FilterExpression': '#type = :type',
                'ExpressionAttributeNames': {'#type': 'Type'},
                'ExpressionAttributeValues': {':type': 'MEMBER'},
                'Limit': limit
            }
            
            if last_key:
                scan_params['ExclusiveStartKey'] = {'PK': f'M#{last_key}', 'SK': f'M#{last_key}'}
            
            response = self.table.scan(**scan_params)
            
            members = [Member.from_dynamodb_item(item) for item in response['Items']]
            
            return {
                'members': members,
                'last_key': response.get('LastEvaluatedKey', {}).get('PK', '').replace('M#', '') if 'LastEvaluatedKey' in response else None,
                'has_more': 'LastEvaluatedKey' in response
            }
            
        except ClientError as e:
            print(f"Error listing members: {e}")
            return {'members': [], 'last_key': None, 'has_more': False}
    
    async def get_active_members(self, limit: int = 50) -> List[Member]:
        """Get all active members"""
        try:
            response = self.table.scan(
                FilterExpression='#type = :type AND #status = :status',
                ExpressionAttributeNames={
                    '#type': 'Type',
                    '#status': 'Status'
                },
                ExpressionAttributeValues={
                    ':type': 'MEMBER',
                    ':status': 'active'
                },
                Limit=limit
            )
            
            return [Member.from_dynamodb_item(item) for item in response['Items']]
            
        except ClientError as e:
            print(f"Error getting active members: {e}")
            return []

class DynamoEmployeeRepository(EmployeeRepository):
    """DynamoDB implementation of EmployeeRepository"""
    
    def __init__(self, table_name: str = 'lms-main', region: str = 'us-east-1'):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    async def create_employee(self, employee: Employee) -> Employee:
        """Create a new employee"""
        employee.created_at = datetime.utcnow()
        employee.updated_at = datetime.utcnow()
        
        try:
            self.table.put_item(Item=employee.to_dynamodb_item())
            return employee
        except ClientError as e:
            print(f"Error creating employee: {e}")
            raise
    
    async def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        try:
            response = self.table.get_item(
                Key={'PK': f'E#{employee_id}', 'SK': f'E#{employee_id}'}
            )
            
            if 'Item' in response:
                return Employee.from_dynamodb_item(response['Item'])
            return None
            
        except ClientError as e:
            print(f"Error getting employee {employee_id}: {e}")
            return None
    
    async def search_employees(self, query: str, limit: int = 10) -> List[EmployeeSearchResult]:
        """Search employees for selection"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :search AND begins_with(GSI1SK, :query)',
                ExpressionAttributeValues={
                    ':search': 'SEARCH',
                    ':query': query.strip().lower()
                },
                Limit=limit,
                ProjectionExpression='Id, FN, LN, Pos'
            )
            
            results = []
            for item in response['Items']:
                # Only include items that are employees (have Pos field)
                if item.get('Pos'):
                    full_name = f"{item.get('FN', '')} {item.get('LN', '')}".strip()
                    results.append(EmployeeSearchResult(
                        id=item['Id'],
                        full_name=full_name,
                        position=item['Pos']
                    ))
            
            return results
            
        except ClientError as e:
            print(f"Error searching employees: {e}")
            return []
    
    async def update_employee(self, employee: Employee) -> Employee:
        """Update existing employee"""
        employee.updated_at = datetime.utcnow()
        
        try:
            self.table.put_item(Item=employee.to_dynamodb_item())
            return employee
        except ClientError as e:
            print(f"Error updating employee: {e}")
            raise
    
    async def list_employees(self) -> List[Employee]:
        """List all employees (small dataset)"""
        try:
            response = self.table.scan(
                FilterExpression='#type = :type',
                ExpressionAttributeNames={'#type': 'Type'},
                ExpressionAttributeValues={':type': 'EMPLOYEE'}
            )
            
            return [Employee.from_dynamodb_item(item) for item in response['Items']]
            
        except ClientError as e:
            print(f"Error listing employees: {e}")
            return []