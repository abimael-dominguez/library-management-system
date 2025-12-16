#!/usr/bin/env python3
"""
CSV to DynamoDB Data Transformation Script
Converts library-cbg-clean.csv to DynamoDB item format for seeding
"""

import csv
import json
import uuid
from datetime import datetime
from typing import Dict, List, Set
from pathlib import Path

def generate_id() -> str:
    """Generate a short UUID for entity IDs"""
    return str(uuid.uuid4())[:8]

def normalize_name(name: str) -> str:
    """Normalize names for consistent storage"""
    if not name or name in ['-', '']:
        return None
    return name.strip()

def normalize_status(status: str) -> str:
    """Map Spanish status to English"""
    status_map = {
        'Prestado': 'loaned',
        'Entregado': 'available',
        'Prestamo': 'loaned'
    }
    return status_map.get(status, 'available')

def parse_date(date_str: str) -> str:
    """Parse date string to ISO format"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        # Handle different date formats in CSV
        if '/' in date_str:
            # Format: MM/DD/YYYY or DD/MM/YYYY
            parts = date_str.split('/')
            if len(parts) == 3:
                return f"20{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        else:
            # Format: YYYY-MM-DD
            return date_str
    except:
        return None

class LibraryDataTransformer:
    def __init__(self):
        self.books: Dict[str, Dict] = {}
        self.members: Dict[str, Dict] = {}
        self.employees: Dict[str, Dict] = {}
        self.copies: List[Dict] = []
        self.loans: List[Dict] = []
        
        # Track unique entities
        self.book_titles: Set[str] = set()
        self.member_names: Set[str] = set()
        self.employee_names: Set[str] = set()
        
        self.current_time = datetime.utcnow().isoformat() + 'Z'

    def process_csv(self, csv_path: str) -> Dict[str, List]:
        """Process CSV file and generate DynamoDB items"""
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                self._process_row(row)
        
        return self._generate_dynamodb_items()

    def _process_row(self, row: Dict[str, str]):
        """Process a single CSV row"""
        
        # Extract and clean data
        title = row['title'].strip()
        author = row['author'].strip()
        total_copies = int(row['total_copies']) if row['total_copies'] else 1
        pages = int(row['pages']) if row['pages'] else None
        max_loan_weeks = int(row['max_loan_weeks']) if row['max_loan_weeks'] else 2
        status = normalize_status(row['status'])
        employee_name = normalize_name(row['employee'])
        member_name = normalize_name(row['member'])
        loan_date = parse_date(row['loan_date'])
        due_date = parse_date(row['due_date'])
        actual_return_date = parse_date(row['actual_return_date'])
        
        # Create or get book
        book_key = f"{title}#{author}"
        if book_key not in self.books:
            book_id = generate_id()
            self.books[book_key] = {
                'book_id': book_id,
                'title': title,
                'author': author,
                'pages': pages,
                'max_loan_weeks': max_loan_weeks,
                'total_copies': total_copies,
                'available_copies': total_copies if status == 'available' else total_copies - 1
            }
        else:
            # Update available copies count
            if status == 'loaned':
                self.books[book_key]['available_copies'] -= 1

        book_id = self.books[book_key]['book_id']
        
        # Create book copy
        copy_id = generate_id()
        copy_item = {
            'copy_id': copy_id,
            'book_id': book_id,
            'status': status
        }
        self.copies.append(copy_item)
        
        # Create member if exists
        member_id = None
        if member_name:
            if member_name not in self.members:
                member_id = generate_id()
                # Parse member info (some entries have phone/address)
                member_parts = member_name.split(',')
                first_name = member_parts[0].strip()
                
                # Extract phone and address if present
                phone = None
                address = None
                if len(member_parts) > 1:
                    for part in member_parts[1:]:
                        part = part.strip()
                        if part.isdigit() or (len(part) == 10 and part.replace(' ', '').isdigit()):
                            phone = part
                        elif len(part) > 10:
                            address = part
                
                self.members[member_name] = {
                    'member_id': member_id,
                    'first_name': first_name,
                    'last_name': '',  # Not separated in CSV
                    'email': f"{first_name.lower().replace(' ', '.')}@example.com",
                    'phone': phone,
                    'address': address,
                    'status': 'active'
                }
            else:
                member_id = self.members[member_name]['member_id']
        
        # Create employee if exists
        employee_id = None
        if employee_name:
            if employee_name not in self.employees:
                employee_id = generate_id()
                name_parts = employee_name.split(' ')
                first_name = name_parts[0] if name_parts else employee_name
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                self.employees[employee_name] = {
                    'employee_id': employee_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'position': 'Librarian'
                }
            else:
                employee_id = self.employees[employee_name]['employee_id']
        
        # Create loan if there's loan data
        if loan_date and member_id:
            loan_status = 'returned' if actual_return_date else ('in_progress' if status == 'loaned' else 'returned')
            
            loan_item = {
                'loan_id': generate_id(),
                'copy_id': copy_id,
                'book_id': book_id,
                'book_title': title,
                'member_id': member_id,
                'member_name': member_name,
                'employee_id': employee_id,
                'employee_name': employee_name,
                'loan_date': loan_date,
                'due_date': due_date,
                'actual_return_date': actual_return_date,
                'status': loan_status
            }
            self.loans.append(loan_item)

    def _generate_dynamodb_items(self) -> Dict[str, List]:
        """Generate DynamoDB items from processed data"""
        
        items = []
        
        # Generate Book items (Cost-Optimized)
        for book_data in self.books.values():
            book_item = {
                'PK': f"B#{book_data['book_id']}",
                'SK': f"B#{book_data['book_id']}",
                'Type': 'BOOK',
                'Id': book_data['book_id'],
                'T': book_data['title'],  # Shortened attribute names
                'A': book_data['author'],
                'Pages': book_data['pages'],
                'MaxWeeks': book_data['max_loan_weeks'],
                'Copies': book_data['total_copies'],
                'Avail': book_data['available_copies'],
                'Created': self.current_time,
                'Updated': self.current_time,
                # Single GSI for search (autocomplete optimized)
                'GSI1PK': 'SEARCH',
                'GSI1SK': f"{book_data['title']}#{book_data['author']}"
            }
            items.append(book_item)
        
        # Generate Copy items (Cost-Optimized)
        for copy_data in self.copies:
            copy_item = {
                'PK': f"B#{copy_data['book_id']}",
                'SK': f"C#{copy_data['copy_id']}",
                'Type': 'COPY',
                'Id': copy_data['copy_id'],
                'BookId': copy_data['book_id'],
                'Status': copy_data['status'],
                'Created': self.current_time,
                'Updated': self.current_time
            }
            items.append(copy_item)
        
        # Generate Member items (Cost-Optimized)
        for member_data in self.members.values():
            member_item = {
                'PK': f"M#{member_data['member_id']}",
                'SK': f"M#{member_data['member_id']}",
                'Type': 'MEMBER',
                'Id': member_data['member_id'],
                'FN': member_data['first_name'],  # Shortened attributes
                'LN': member_data['last_name'],
                'Email': member_data['email'],
                'Phone': member_data['phone'],
                'Addr': member_data['address'],
                'Status': member_data['status'],
                'RegDate': '2025-01-01',
                'Created': self.current_time,
                'Updated': self.current_time,
                # Single GSI for member search
                'GSI1PK': 'SEARCH',
                'GSI1SK': f"{member_data['first_name']} {member_data['last_name']}#{member_data['email']}"
            }
            items.append(member_item)
        
        # Generate Employee items (Cost-Optimized)
        for employee_data in self.employees.values():
            employee_item = {
                'PK': f"E#{employee_data['employee_id']}",
                'SK': f"E#{employee_data['employee_id']}",
                'Type': 'EMPLOYEE',
                'Id': employee_data['employee_id'],
                'FN': employee_data['first_name'],
                'LN': employee_data['last_name'],
                'Pos': employee_data['position'],
                'Created': self.current_time,
                'Updated': self.current_time,
                # Add to search for employee selection
                'GSI1PK': 'SEARCH',
                'GSI1SK': f"{employee_data['first_name']} {employee_data['last_name']}#employee"
            }
            items.append(employee_item)
        
        # Generate Loan items (Cost-Optimized with Smart Denormalization)
        for loan_data in self.loans:
            loan_item = {
                'PK': f"L#{loan_data['loan_id']}",
                'SK': f"L#{loan_data['loan_id']}",
                'Type': 'LOAN',
                'Id': loan_data['loan_id'],
                'CopyId': loan_data['copy_id'],
                'BookId': loan_data['book_id'],
                'BookTitle': loan_data['book_title'],  # Denormalized for UX
                'MemberId': loan_data['member_id'],
                'MemberName': loan_data['member_name'],  # Denormalized for UX
                'EmployeeId': loan_data['employee_id'],
                'EmployeeName': loan_data['employee_name'],
                'LoanDate': loan_data['loan_date'],
                'DueDate': loan_data['due_date'],
                'ReturnDate': loan_data['actual_return_date'],
                'Status': loan_data['status'],
                'Created': self.current_time,
                'Updated': self.current_time,
                # Single GSI for status queries (overdue loans)
                'GSI1PK': 'STATUS',
                'GSI1SK': f"{loan_data['status']}#{loan_data['due_date'] or loan_data['loan_date']}"
            }
            items.append(loan_item)
        
        return {
            'items': items,
            'summary': {
                'total_items': len(items),
                'books': len(self.books),
                'copies': len(self.copies),
                'members': len(self.members),
                'employees': len(self.employees),
                'loans': len(self.loans)
            }
        }

def batch_write_to_dynamodb(items, table_name='lms-main'):
    """Write items to DynamoDB using batch operations for cost optimization"""
    try:
        import boto3
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Process in batches of 25 (DynamoDB limit)
        batch_count = 0
        total_items = len(items)
        
        for i in range(0, total_items, 25):
            batch = items[i:i+25]
            batch_count += 1
            
            with table.batch_writer() as batch_writer:
                for item in batch:
                    batch_writer.put_item(Item=item)
            
            print(f"📦 Batch {batch_count} written ({len(batch)} items)")
        
        cost_savings = ((total_items - batch_count) / total_items * 100) if total_items > batch_count else 0
        print(f"💰 Cost optimization: {cost_savings:.1f}% fewer requests ({batch_count} vs {total_items})")
        
        return batch_count
    except ImportError:
        print("⚠️  boto3 not available. Install with: pip install boto3")
        return 0

def main():
    """Main function to process CSV and generate DynamoDB data"""
    
    # Paths
    csv_path = Path(__file__).parent.parent.parent / 'external' / 'library-management-system' / 'data' / 'library-cbg-clean.csv'
    output_path = Path(__file__).parent.parent / 'data' / 'dynamodb-seed-data.json'
    
    # Ensure output directory exists
    output_path.parent.mkdir(exist_ok=True)
    
    # Process CSV
    transformer = LibraryDataTransformer()
    result = transformer.process_csv(csv_path)
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Print summary
    summary = result['summary']
    print("✅ CSV to DynamoDB transformation completed (Cost-Optimized)!")
    print(f"📊 Summary:")
    print(f"   - Total items: {summary['total_items']}")
    print(f"   - Books: {summary['books']}")
    print(f"   - Copies: {summary['copies']}")
    print(f"   - Members: {summary['members']}")
    print(f"   - Employees: {summary['employees']}")
    print(f"   - Loans: {summary['loans']}")
    print(f"📁 Output saved to: {output_path}")
    print(f"\n🎯 Optimizations Applied:")
    print(f"   - Single GSI design (reduced cost)")
    print(f"   - Shortened attribute names (smaller items)")
    print(f"   - Smart denormalization (better UX)")
    print(f"   - Batch write ready (96% cost reduction)")
    print(f"\n💡 To write to DynamoDB with batch optimization:")
    print(f"   batch_write_to_dynamodb(result['items'])")
    
    return result

if __name__ == '__main__':
    main()