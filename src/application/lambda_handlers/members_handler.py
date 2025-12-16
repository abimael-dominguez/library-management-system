import json
import asyncio
from typing import Dict, Any

from ...infrastructure.dynamodb.member_repository_impl import DynamoMemberRepository
from ...application.use_cases.member_service import MemberService
from ...application.dto.member_dto import CreateMemberRequest


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    return asyncio.run(async_handler(event, context))


async def async_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        member_repo = DynamoMemberRepository()
        member_service = MemberService(member_repo)
        
        http_method = event['httpMethod']
        path = event['path']
        query_params = event.get('queryStringParameters') or {}
        
        if http_method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        if path == '/members' and http_method == 'GET':
            limit = int(query_params.get('limit', 50))
            last_key = query_params.get('lastKey')
            members, next_key = await member_service.list_members(limit, last_key)
            
            response_body = {
                'members': [member.dict() for member in members],
                'nextKey': next_key
            }
            
        elif path == '/members' and http_method == 'POST':
            body = json.loads(event['body'])
            request = CreateMemberRequest(**body)
            member = await member_service.create_member(request)
            response_body = member.dict()
            
        elif path.startswith('/members/') and http_method == 'GET':
            member_id = path.split('/')[-1]
            member = await member_service.get_member(member_id)
            if not member:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': 'Member not found'})
                }
            response_body = member.dict()
            
        elif path == '/autocomplete' and http_method == 'GET' and query_params.get('type') == 'member':
            query = query_params.get('q', '')
            limit = int(query_params.get('limit', 5))
            
            if not query:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Query parameter q is required'})
                }
            
            results = await member_service.autocomplete_members(query, limit)
            response_body = {'results': results}
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