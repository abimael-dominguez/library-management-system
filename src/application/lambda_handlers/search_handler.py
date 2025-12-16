"""
Search Lambda Handler - Ultra-Fast Autocomplete API
"""

import json
import asyncio
from typing import Dict, Any
from ...infrastructure.dynamodb.search_repository_impl import DynamoSearchRepository
from ..use_cases.search_service import SearchService
from ..dtos.search_dto import AutocompleteRequest, SearchEntityType

# Initialize dependencies (reused across Lambda invocations)
search_repository = DynamoSearchRepository()
search_service = SearchService(search_repository)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for search operations
    
    Routes:
    - GET /search?q=query&type=book&limit=10 - Autocomplete search
    - GET /search/suggestions?q=partial - Get search suggestions
    - GET /search/all?q=query - Search across all entity types
    """
    
    try:
        # Extract request info
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        query_params = event.get('queryStringParameters') or {}
        
        # CORS headers for all responses
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }
        
        # Handle OPTIONS for CORS
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Route to appropriate handler
        if path.endswith('/suggestions'):
            return asyncio.run(handle_suggestions(query_params, headers))
        elif path.endswith('/all'):
            return asyncio.run(handle_unified_search(query_params, headers))
        else:
            return asyncio.run(handle_autocomplete(query_params, headers))
            
    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

async def handle_autocomplete(query_params: Dict[str, str], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle autocomplete search requests"""
    
    # Validate required parameters
    query = query_params.get('q', '').strip()
    if not query:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Missing required parameter: q (query)'
            })
        }
    
    # Parse optional parameters
    entity_type_str = query_params.get('type', 'book').lower()
    limit = min(int(query_params.get('limit', 10)), 20)  # Max 20 for performance
    
    # Map entity type
    entity_type_map = {
        'book': SearchEntityType.BOOK,
        'member': SearchEntityType.MEMBER,
        'employee': SearchEntityType.EMPLOYEE
    }
    
    entity_type = entity_type_map.get(entity_type_str, SearchEntityType.BOOK)
    
    # Create request and execute search
    request = AutocompleteRequest(
        query=query,
        entity_type=entity_type,
        limit=limit
    )
    
    response = await search_service.autocomplete(request)
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': response.json()
    }

async def handle_suggestions(query_params: Dict[str, str], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle search suggestions requests"""
    
    query = query_params.get('q', '').strip()
    if len(query) < 2:
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'suggestions': [],
                'query': query
            })
        }
    
    limit = min(int(query_params.get('limit', 5)), 10)
    suggestions = await search_service.get_suggestions(query, limit)
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'suggestions': suggestions,
            'query': query,
            'total': len(suggestions)
        })
    }

async def handle_unified_search(query_params: Dict[str, str], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle unified search across all entity types"""
    
    query = query_params.get('q', '').strip()
    if not query:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Missing required parameter: q (query)'
            })
        }
    
    limit_per_type = min(int(query_params.get('limit', 5)), 10)
    results = await search_service.unified_search(query, limit_per_type)
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(results)
    }

# Health check endpoint
def health_check() -> Dict[str, Any]:
    """Health check for the search service"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'service': 'search',
            'status': 'healthy',
            'version': '1.0.0',
            'features': [
                'autocomplete',
                'suggestions', 
                'unified_search'
            ]
        })
    }