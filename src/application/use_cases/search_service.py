"""
Search Service - Ultra-Fast Autocomplete Use Cases
"""

import time
from typing import List
from ...infrastructure.dynamodb.search_repository_impl import DynamoSearchRepository
from ..dtos.search_dto import (
    AutocompleteRequest, AutocompleteResponse, AdvancedSearchRequest, 
    AdvancedSearchResponse, SearchEntityType, AutocompleteResultItem
)

class SearchService:
    """Service for handling all search operations with performance monitoring"""
    
    def __init__(self, search_repository: DynamoSearchRepository):
        self.search_repository = search_repository
    
    def search_books(self, query: str, limit: int = 10) -> List:
        """Synchronous book search for testing"""
        if not query or len(query.strip()) < 2:
            return []
        
        try:
            return self.search_repository.search_books(query.strip(), limit)
        except Exception as e:
            print(f"Error in search_books: {str(e)}")
            return []
    
    def search_members(self, query: str, limit: int = 10) -> List:
        """Synchronous member search for testing"""
        if not query or len(query.strip()) < 2:
            return []
        
        try:
            return self.search_repository.search_members(query.strip(), limit)
        except Exception as e:
            print(f"Error in search_members: {str(e)}")
            return []
    
    async def autocomplete(self, request: AutocompleteRequest) -> AutocompleteResponse:
        """Ultra-fast autocomplete with performance monitoring"""
        start_time = time.time()
        
        try:
            results = await self.search_repository.search_unified(
                query=request.query,
                entity_type=request.entity_type,
                limit=request.limit
            )
            
            query_time_ms = (time.time() - start_time) * 1000
            
            return AutocompleteResponse(
                results=results,
                total=len(results),
                query=request.query,
                entity_type=request.entity_type,
                query_time_ms=round(query_time_ms, 2)
            )
            
        except Exception as e:
            print(f"Autocomplete error: {e}")
            query_time_ms = (time.time() - start_time) * 1000
            
            return AutocompleteResponse(
                results=[],
                total=0,
                query=request.query,
                entity_type=request.entity_type,
                query_time_ms=round(query_time_ms, 2)
            )
    
    async def search_books_fast(self, query: str, limit: int = 10) -> List[AutocompleteResultItem]:
        """Fast book search for loan/return workflow"""
        return await self.search_repository.search_unified(
            query=query,
            entity_type=SearchEntityType.BOOK,
            limit=limit
        )
    
    async def search_members_fast(self, query: str, limit: int = 10) -> List[AutocompleteResultItem]:
        """Fast member search for loan workflow"""
        return await self.search_repository.search_unified(
            query=query,
            entity_type=SearchEntityType.MEMBER,
            limit=limit
        )
    
    async def search_employees_fast(self, query: str, limit: int = 5) -> List[AutocompleteResultItem]:
        """Fast employee search for loan processing"""
        return await self.search_repository.search_unified(
            query=query,
            entity_type=SearchEntityType.EMPLOYEE,
            limit=limit
        )
    
    async def unified_search(self, query: str, limit_per_type: int = 5) -> dict:
        """Search across all entity types for comprehensive results"""
        start_time = time.time()
        
        try:
            results = await self.search_repository.search_all_entities(
                query=query,
                limit_per_type=limit_per_type
            )
            
            query_time_ms = (time.time() - start_time) * 1000
            results['query_time_ms'] = round(query_time_ms, 2)
            
            return results
            
        except Exception as e:
            print(f"Unified search error: {e}")
            query_time_ms = (time.time() - start_time) * 1000
            
            return {
                'books': [],
                'members': [],
                'employees': [],
                'total_results': 0,
                'query_time_ms': round(query_time_ms, 2)
            }
    
    async def get_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions for autocomplete dropdown"""
        if len(partial_query) < 2:  # Don't suggest for very short queries
            return []
        
        return await self.search_repository.get_search_suggestions(
            partial_query=partial_query,
            limit=limit
        )
    
    async def advanced_search(self, request: AdvancedSearchRequest) -> AdvancedSearchResponse:
        """Advanced search with filters (future enhancement)"""
        start_time = time.time()
        
        # For now, delegate to basic search
        # TODO: Implement filtering logic
        basic_results = await self.search_repository.search_unified(
            query=request.query or "",
            entity_type=request.entity_type,
            limit=request.limit
        )
        
        query_time_ms = (time.time() - start_time) * 1000
        
        return AdvancedSearchResponse(
            results=basic_results,
            total=len(basic_results),
            query=request.query,
            filters=request.filters,
            limit=request.limit,
            offset=request.offset,
            has_more=False,  # Will be calculated properly when pagination is implemented
            query_time_ms=round(query_time_ms, 2)
        )