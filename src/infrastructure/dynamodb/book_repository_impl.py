import os
from typing import List, Optional
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

from domain.entities.book import Book, BookCopy, BookStatus
from domain.repositories.book_repository import BookRepository, BookCopyRepository


class DynamoBookRepository(BookRepository):
    def __init__(self, table_name: str = None, dynamodb=None):
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE', 'lms-table')
        self.dynamodb = dynamodb or boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    async def create_book(self, book: Book) -> Book:
        item = {
            'pk': f'BOOK#{book.book_id}',
            'sk': 'METADATA',
            'gsi1pk': 'SEARCH#book',
            'gsi1sk': f"{book.title.lower()} {book.author.lower()}",
            'entity_type': 'book',
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'publisher': book.publisher,
            'publication_year': book.publication_year,
            'genre': book.genre,
            'pages': book.pages,
            'max_loan_weeks': book.max_loan_weeks,
            'total_copies': book.total_copies,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        }
        
        # Remove None values
        item = {k: v for k, v in item.items() if v is not None}
        
        self.table.put_item(Item=item)
        return book

    async def get_book_by_id(self, book_id: str) -> Optional[Book]:
        response = self.table.get_item(
            Key={'pk': f'BOOK#{book_id}', 'sk': 'METADATA'}
        )
        
        if 'Item' not in response:
            return None
            
        item = response['Item']
        return self._item_to_book(item)

    async def search_books(self, query: str, limit: int = 10) -> List[Book]:
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('gsi1pk').eq('SEARCH#book') & Key('gsi1sk').begins_with(query.lower()),
            Limit=limit
        )
        
        return [self._item_to_book(item) for item in response.get('Items', [])]

    async def autocomplete_books(self, query: str, limit: int = 5) -> List[dict]:
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('gsi1pk').eq('SEARCH#book') & Key('gsi1sk').begins_with(query.lower()),
            Limit=limit,
            ProjectionExpression='book_id, title, author'
        )
        
        return [{'id': item['book_id'], 'title': item['title'], 'author': item['author']} 
                for item in response.get('Items', [])]

    async def list_books(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[Book], Optional[str]]:
        kwargs = {
            'IndexName': 'GSI1',
            'KeyConditionExpression': Key('gsi1pk').eq('SEARCH#book'),
            'Limit': limit
        }
        
        if last_key:
            kwargs['ExclusiveStartKey'] = {'gsi1pk': 'SEARCH#book', 'gsi1sk': last_key}
        
        response = self.table.query(**kwargs)
        books = [self._item_to_book(item) for item in response.get('Items', [])]
        
        next_key = None
        if 'LastEvaluatedKey' in response:
            next_key = response['LastEvaluatedKey']['gsi1sk']
        
        return books, next_key

    async def update_book(self, book: Book) -> Book:
        return await self.create_book(book)  # DynamoDB put_item updates if exists

    async def delete_book(self, book_id: str) -> bool:
        try:
            self.table.delete_item(
                Key={'pk': f'BOOK#{book_id}', 'sk': 'METADATA'}
            )
            return True
        except Exception:
            return False

    def _item_to_book(self, item: dict) -> Book:
        return Book(
            book_id=item['book_id'],
            title=item['title'],
            author=item['author'],
            isbn=item.get('isbn'),
            publisher=item.get('publisher'),
            publication_year=item.get('publication_year'),
            genre=item.get('genre'),
            pages=item.get('pages'),
            max_loan_weeks=item.get('max_loan_weeks', 3),
            total_copies=item.get('total_copies', 1),
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None
        )


class DynamoBookCopyRepository(BookCopyRepository):
    def __init__(self, table_name: str = None, dynamodb=None):
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE', 'lms-table')
        self.dynamodb = dynamodb or boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    async def create_book_copy(self, book_copy: BookCopy) -> BookCopy:
        item = {
            'pk': f'BOOK#{book_copy.book_id}',
            'sk': f'COPY#{book_copy.book_copy_id}',
            'entity_type': 'book_copy',
            'book_copy_id': book_copy.book_copy_id,
            'book_id': book_copy.book_id,
            'status': book_copy.status.value,
            'created_at': book_copy.created_at.isoformat() if book_copy.created_at else None,
            'updated_at': book_copy.updated_at.isoformat() if book_copy.updated_at else None
        }
        
        item = {k: v for k, v in item.items() if v is not None}
        self.table.put_item(Item=item)
        return book_copy

    async def get_book_copy_by_id(self, book_copy_id: str) -> Optional[BookCopy]:
        # Extract book_id from book_copy_id (format: book_id-001)
        book_id = book_copy_id.rsplit('-', 1)[0]
        
        response = self.table.get_item(
            Key={'pk': f'BOOK#{book_id}', 'sk': f'COPY#{book_copy_id}'}
        )
        
        if 'Item' not in response:
            return None
            
        return self._item_to_book_copy(response['Item'])

    async def get_copies_by_book_id(self, book_id: str) -> List[BookCopy]:
        response = self.table.query(
            KeyConditionExpression=Key('pk').eq(f'BOOK#{book_id}') & Key('sk').begins_with('COPY#')
        )
        
        return [self._item_to_book_copy(item) for item in response.get('Items', [])]

    async def update_book_copy(self, book_copy: BookCopy) -> BookCopy:
        return await self.create_book_copy(book_copy)

    def _item_to_book_copy(self, item: dict) -> BookCopy:
        return BookCopy(
            book_copy_id=item['book_copy_id'],
            book_id=item['book_id'],
            status=BookStatus(item['status']),
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None
        )