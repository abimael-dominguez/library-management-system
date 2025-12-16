"""
Members Lambda Handler
Handles member CRUD operations
"""
import json
import os
from typing import Dict, Any
from infrastructure.dynamodb.member_repository_impl import DynamoMemberRepository
from domain.entities.member import Member


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle member operations"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Initialize repository
        table_name = os.environ['DYNAMODB_TABLE']
        member_repo = DynamoMemberRepository(table_name)
        
        http_method = event['httpMethod']
        path_params = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        
        if http_method == 'GET':
            if 'member_id' in path_params:
                # Get single member
                member_id = path_params['member_id']
                member = member_repo.get_by_id(member_id)
                
                if not member:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({'error': 'Member not found'})
                    }
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(member.to_dict())
                }
            else:
                # List members with pagination
                limit = int(query_params.get('limit', 20))
                last_key = query_params.get('last_key')
                
                members, next_key = member_repo.list_members(limit, last_key)
                
                response_data = {
                    'members': [member.to_dict() for member in members],
                    'next_key': next_key
                }
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(response_data)
                }
        
        elif http_method == 'POST':
            # Create new member
            body = json.loads(event['body'])
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in body:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({'error': f'Missing required field: {field}'})
                    }
            
            # Create member entity
            member = Member(
                member_id=None,  # Will be generated
                first_name=body['first_name'],
                last_name=body['last_name'],
                email=body['email'],
                address=body.get('address', ''),
                phone=body.get('phone', ''),
                status='active'
            )
            
            # Save member
            saved_member = member_repo.save(member)
            
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps(saved_member.to_dict())
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
        print(f"Error in members_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }