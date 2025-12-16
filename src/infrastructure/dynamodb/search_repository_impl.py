"""
DynamoDB Search Repository - Ultra-Fast Autocomplete Implementation
"""

import boto3
from typing import List, Union
from botocore.exceptions import ClientError

from ...application.dtos.search_dto import (
    SearchEntityType, BookAutocompleteResult, MemberAutocompleteResult, 
    EmployeeAutocompleteResult, AutocompleteResultItem
)

class DynamoSearchRepository:
    """Unified search repository for ultra-fast autocomplete across all entities"""
    
    def __init__(self, table_name: str = 'lms-main', region: str = 'us-east-1'):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    async def search_unified(
        self, 
        query: str, 
        entity_type: SearchEntityType, 
        limit: int = 10
    ) -> List[AutocompleteResultItem]:
        """Unified search across all entity types using single GSI"""
        
        if entity_type == SearchEntityType.BOOK:
            return await self._search_books(query, limit)
        elif entity_type == SearchEntityType.MEMBER:
            return await self._search_members(query, limit)
        elif entity_type == SearchEntityType.EMPLOYEE:
            return await self._search_employees(query, limit)
        else:
            return []
    
    async def _search_books(self, query: str, limit: int) -> List[BookAutocompleteResult]:
        """Search books for autocomplete"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :search AND begins_with(GSI1SK, :query)',
                ExpressionAttributeValues={
                    ':search': 'SEARCH',
                    ':query': query.strip().lower()
                },
                Limit=limit,
                ProjectionExpression='Id, T, A, Avail, Copies, ISBN'
            )
            
            results = []
            for item in response['Items']:
                # Only include items that are actually books
                if item.get('T') and item.get('A'):  # Has title and author
                    results.append(BookAutocompleteResult(
                        id=item['Id'],
                        title=item['T'],
                        author=item['A'],
                        available_copies=item.get('Avail', 0),
                        total_copies=item.get('Copies', 1),
                        isbn=item.get('ISBN')
                    ))
            
            return results
            
        except ClientError as e:
            print(f"Error searching books: {e}")
            return []
    
    async def _search_members(self, query: str, limit: int) -> List[MemberAutocompleteResult]:
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
                # Only include items that are members (have FN, LN, Email)
                if item.get('FN') and item.get('Email') and '@' in item.get('Email', ''):
                    full_name = f"{item['FN']} {item.get('LN', '')}".strip()
                    results.append(MemberAutocompleteResult(
                        id=item['Id'],
                        full_name=full_name,
                        email=item['Email'],
                        status=item.get('Status', 'active')
                    ))
            
            return results
            
        except ClientError as e:
            print(f"Error searching members: {e}")
            return []
    
    async def _search_employees(self, query: str, limit: int) -> List[EmployeeAutocompleteResult]:
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
                if item.get('Pos') and item.get('FN'):
                    full_name = f"{item['FN']} {item.get('LN', '')}".strip()
                    results.append(EmployeeAutocompleteResult(
                        id=item['Id'],
                        full_name=full_name,
                        position=item['Pos']
                    ))
            
            return results
            
        except ClientError as e:
            print(f"Error searching employees: {e}")
            return []
    
    async def search_all_entities(self, query: str, limit_per_type: int = 5) -> dict:
        """Search across all entity types for comprehensive results"""
        try:
            # Single query to GSI1 to get all matching items
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :search AND begins_with(GSI1SK, :query)',
                ExpressionAttributeValues={
                    ':search': 'SEARCH',
                    ':query': query.strip().lower()
                },
                Limit=limit_per_type * 3  # Get more items to filter by type
            )
            
            books = []
            members = []
            employees = []
            
            for item in response['Items']:
                # Determine entity type by available fields
                if item.get('T') and item.get('A'):  # Book
                    if len(books) < limit_per_type:
                        books.append(BookAutocompleteResult(
                            id=item['Id'],
                            title=item['T'],
                            author=item['A'],
                            available_copies=item.get('Avail', 0),
                            total_copies=item.get('Copies', 1),
                            isbn=item.get('ISBN')
                        ))
                
                elif item.get('Email') and '@' in item.get('Email', ''):  # Member
                    if len(members) < limit_per_type:
                        full_name = f"{item.get('FN', '')} {item.get('LN', '')}".strip()
                        members.append(MemberAutocompleteResult(
                            id=item['Id'],
                            full_name=full_name,
                            email=item['Email'],
                            status=item.get('Status', 'active')
                        ))
                
                elif item.get('Pos'):  # Employee
                    if len(employees) < limit_per_type:
                        full_name = f"{item.get('FN', '')} {item.get('LN', '')}".strip()
                        employees.append(EmployeeAutocompleteResult(
                            id=item['Id'],
                            full_name=full_name,
                            position=item['Pos']
                        ))
            
            return {
                'books': books,
                'members': members,
                'employees': employees,
                'total_results': len(books) + len(members) + len(employees)
            }
            
        except ClientError as e:
            print(f"Error in unified search: {e}")
            return {'books': [], 'members': [], 'employees': [], 'total_results': 0}
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on partial input"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :search AND begins_with(GSI1SK, :query)',
                ExpressionAttributeValues={
                    ':search': 'SEARCH',
                    ':query': partial_query.strip().lower()
                },
                Limit=limit,
                ProjectionExpression='GSI1SK'
            )
            
            suggestions = []
            for item in response['Items']:
                # Extract the first part (title or name) from the sort key
                sort_key = item['GSI1SK']
                if '#' in sort_key:
                    suggestion = sort_key.split('#')[0]
                    if suggestion not in suggestions:
                        suggestions.append(suggestion)
            
            return suggestions[:limit]
            
        except ClientError as e:
            print(f"Error getting suggestions: {e}")
            return []