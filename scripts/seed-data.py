#!/usr/bin/env python3
"""
Script to seed the DynamoDB table with initial data from CSV
"""
import csv
import json
import uuid
import boto3
from datetime import datetime, date, timedelta
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from domain.entities.book import Book, BookCopy, BookStatus
from domain.entities.member import Member, MemberStatus
from domain.entities.employee import Employee
from domain.entities.loan import Loan, LoanStatus


def create_dynamodb_client(profile_name='immersion', region='us-east-1'):
    """Create DynamoDB client"""
    session = boto3.Session(profile_name=profile_name)
    return session.resource('dynamodb', region_name=region)


def parse_csv_data(csv_file_path):
    """Parse CSV data and return structured data"""
    books = {}
    members = {}
    employees = {}
    loans = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            title = row['title'].strip()
            author = row['author'].strip()
            total_copies = int(row['total_copies']) if row['total_copies'] else 1
            pages = int(row['pages']) if row['pages'] else None
            max_loan_weeks = int(row['max_loan_weeks']) if row['max_loan_weeks'] else 3
            status = row['status'].strip()
            employee_name = row['employee'].strip() if row['employee'] and row['employee'] != '-' else None
            member_name = row['member'].strip() if row['member'] and row['member'] != '-' else None
            loan_date = row['loan_date'].strip() if row['loan_date'] else None
            due_date = row['due_date'].strip() if row['due_date'] else None
            
            # Create book if not exists
            book_key = f"{title}|{author}"
            if book_key not in books:
                book_id = str(uuid.uuid4())
                books[book_key] = {
                    'book_id': book_id,
                    'title': title,
                    'author': author,
                    'pages': pages,
                    'max_loan_weeks': max_loan_weeks,
                    'total_copies': total_copies
                }
            
            # Create employee if exists and not already created
            if employee_name and employee_name not in employees:
                employee_id = str(uuid.uuid4())
                employees[employee_name] = {
                    'employee_id': employee_id,
                    'first_name': employee_name.split()[0],
                    'last_name': ' '.join(employee_name.split()[1:]) if len(employee_name.split()) > 1 else '',
                    'position': 'Librarian'
                }
            
            # Create member if exists and not already created
            if member_name and member_name not in members:
                member_id = str(uuid.uuid4())
                name_parts = member_name.split()
                members[member_name] = {
                    'member_id': member_id,
                    'first_name': name_parts[0],
                    'last_name': ' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                    'email': f"{name_parts[0].lower()}@example.com",
                    'status': MemberStatus.ACTIVE.value
                }
            
            # Create loan if there's loan data
            if status in ['Prestado', 'Prestamo'] and loan_date and member_name:
                loan_id = str(uuid.uuid4())
                book_copy_id = f"{books[book_key]['book_id']}-001"
                
                # Parse dates
                try:
                    loan_date_obj = datetime.strptime(loan_date, '%Y-%m-%d').date()
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else loan_date_obj + timedelta(weeks=max_loan_weeks)
                except:
                    continue  # Skip if date parsing fails
                
                loans.append({
                    'loan_id': loan_id,
                    'book_copy_id': book_copy_id,
                    'member_id': members[member_name]['member_id'],
                    'employee_id': employees[employee_name]['employee_id'] if employee_name else None,
                    'loan_date': loan_date_obj.isoformat(),
                    'due_date': due_date_obj.isoformat(),
                    'status': LoanStatus.IN_PROGRESS.value
                })
    
    return list(books.values()), list(members.values()), list(employees.values()), loans


def seed_dynamodb_table(table_name, books, members, employees, loans):
    """Seed DynamoDB table with data"""
    dynamodb = create_dynamodb_client()
    table = dynamodb.Table(table_name)
    
    print(f"Seeding table: {table_name}")
    
    # Seed books
    print(f"Adding {len(books)} books...")
    for book in books:
        # Add book metadata
        item = {
            'pk': f'BOOK#{book["book_id"]}',
            'sk': 'METADATA',
            'gsi1pk': 'SEARCH#book',
            'gsi1sk': f"{book['title'].lower()} {book['author'].lower()}",
            'entity_type': 'book',
            'book_id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'pages': book['pages'],
            'max_loan_weeks': book['max_loan_weeks'],
            'total_copies': book['total_copies'],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Remove None values
        item = {k: v for k, v in item.items() if v is not None}
        table.put_item(Item=item)
        
        # Add book copies
        for i in range(book['total_copies']):
            copy_id = f"{book['book_id']}-{i+1:03d}"
            copy_item = {
                'pk': f'BOOK#{book["book_id"]}',
                'sk': f'COPY#{copy_id}',
                'entity_type': 'book_copy',
                'book_copy_id': copy_id,
                'book_id': book['book_id'],
                'status': BookStatus.AVAILABLE.value,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            table.put_item(Item=copy_item)
    
    # Seed members
    print(f"Adding {len(members)} members...")
    for member in members:
        item = {
            'pk': f'MEMBER#{member["member_id"]}',
            'sk': 'METADATA',
            'gsi1pk': 'SEARCH#member',
            'gsi1sk': f"{member['first_name'].lower()} {member['last_name'].lower()}",
            'entity_type': 'member',
            'member_id': member['member_id'],
            'first_name': member['first_name'],
            'last_name': member['last_name'],
            'email': member['email'],
            'status': member['status'],
            'registration_date': date.today().isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
    
    # Seed employees
    print(f"Adding {len(employees)} employees...")
    for employee in employees:
        item = {
            'pk': f'EMPLOYEE#{employee["employee_id"]}',
            'sk': 'METADATA',
            'entity_type': 'employee',
            'employee_id': employee['employee_id'],
            'first_name': employee['first_name'],
            'last_name': employee['last_name'],
            'position': employee['position'],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
    
    # Seed loans
    print(f"Adding {len(loans)} loans...")
    for loan in loans:
        item = {
            'pk': f'LOAN#{loan["loan_id"]}',
            'sk': 'METADATA',
            'gsi1pk': f'MEMBER#{loan["member_id"]}',
            'gsi1sk': f'LOAN#{loan["loan_date"]}',
            'entity_type': 'loan',
            'loan_id': loan['loan_id'],
            'book_copy_id': loan['book_copy_id'],
            'member_id': loan['member_id'],
            'employee_id': loan['employee_id'],
            'loan_date': loan['loan_date'],
            'due_date': loan['due_date'],
            'status': loan['status'],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Remove None values
        item = {k: v for k, v in item.items() if v is not None}
        table.put_item(Item=item)
    
    print("Data seeding completed successfully!")


def main():
    csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'library-cbg-clean.csv')
    table_name = 'lms-table-dev'  # Update this based on your deployment
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return
    
    print("Parsing CSV data...")
    books, members, employees, loans = parse_csv_data(csv_file)
    
    print(f"Parsed data:")
    print(f"  - Books: {len(books)}")
    print(f"  - Members: {len(members)}")
    print(f"  - Employees: {len(employees)}")
    print(f"  - Loans: {len(loans)}")
    
    seed_dynamodb_table(table_name, books, members, employees, loans)


if __name__ == '__main__':
    main()