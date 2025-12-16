import os
from typing import List, Optional
from datetime import datetime, date
import boto3
from boto3.dynamodb.conditions import Key, Attr

from ...domain.entities.member import Member, MemberStatus
from ...domain.repositories.member_repository import MemberRepository


class DynamoMemberRepository(MemberRepository):
    def __init__(self, table_name: str = None, dynamodb=None):
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE', 'lms-table')
        self.dynamodb = dynamodb or boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    async def create_member(self, member: Member) -> Member:
        item = {
            'pk': f'MEMBER#{member.member_id}',
            'sk': 'METADATA',
            'gsi1pk': 'SEARCH#member',
            'gsi1sk': f"{member.first_name.lower()} {member.last_name.lower()}",
            'entity_type': 'member',
            'member_id': member.member_id,
            'first_name': member.first_name,
            'last_name': member.last_name,
            'email': member.email,
            'address': member.address,
            'phone': member.phone,
            'registration_date': member.registration_date.isoformat() if member.registration_date else None,
            'status': member.status.value,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'updated_at': member.updated_at.isoformat() if member.updated_at else None
        }
        
        item = {k: v for k, v in item.items() if v is not None}
        self.table.put_item(Item=item)
        return member

    async def get_member_by_id(self, member_id: str) -> Optional[Member]:
        response = self.table.get_item(
            Key={'pk': f'MEMBER#{member_id}', 'sk': 'METADATA'}
        )
        
        if 'Item' not in response:
            return None
            
        return self._item_to_member(response['Item'])

    async def search_members(self, query: str, limit: int = 10) -> List[Member]:
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('gsi1pk').eq('SEARCH#member') & Key('gsi1sk').begins_with(query.lower()),
            Limit=limit
        )
        
        return [self._item_to_member(item) for item in response.get('Items', [])]

    async def autocomplete_members(self, query: str, limit: int = 5) -> List[dict]:
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('gsi1pk').eq('SEARCH#member') & Key('gsi1sk').begins_with(query.lower()),
            Limit=limit,
            ProjectionExpression='member_id, first_name, last_name'
        )
        
        return [{'id': item['member_id'], 'name': f"{item['first_name']} {item['last_name']}"} 
                for item in response.get('Items', [])]

    async def list_members(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[Member], Optional[str]]:
        kwargs = {
            'IndexName': 'GSI1',
            'KeyConditionExpression': Key('gsi1pk').eq('SEARCH#member'),
            'Limit': limit
        }
        
        if last_key:
            kwargs['ExclusiveStartKey'] = {'gsi1pk': 'SEARCH#member', 'gsi1sk': last_key}
        
        response = self.table.query(**kwargs)
        members = [self._item_to_member(item) for item in response.get('Items', [])]
        
        next_key = None
        if 'LastEvaluatedKey' in response:
            next_key = response['LastEvaluatedKey']['gsi1sk']
        
        return members, next_key

    async def update_member(self, member: Member) -> Member:
        return await self.create_member(member)

    async def delete_member(self, member_id: str) -> bool:
        try:
            self.table.delete_item(
                Key={'pk': f'MEMBER#{member_id}', 'sk': 'METADATA'}
            )
            return True
        except Exception:
            return False

    def _item_to_member(self, item: dict) -> Member:
        return Member(
            member_id=item['member_id'],
            first_name=item['first_name'],
            last_name=item['last_name'],
            email=item['email'],
            address=item.get('address'),
            phone=item.get('phone'),
            registration_date=date.fromisoformat(item['registration_date']) if item.get('registration_date') else None,
            status=MemberStatus(item['status']),
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None
        )