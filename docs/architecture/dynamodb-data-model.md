# DynamoDB Data Model Design

## Overview
This document maps the PostgreSQL relational schema to a DynamoDB NoSQL design optimized for the Library Management System's access patterns and cost efficiency.

## SQL to NoSQL Mapping Strategy

### Key Design Principles
1. **Single Table Design**: Use one main table with GSIs for different access patterns
2. **Cost Optimization**: Minimal GSIs, optimized for ~500 items initially
3. **Access Pattern Driven**: Design based on actual LMS workflows
4. **Denormalization**: Store related data together to reduce queries

## Access Patterns Analysis

Based on the CSV data and LMS requirements, the critical access patterns are:

### Primary Access Patterns
1. **Search books by title/author** (autocomplete)
2. **Get book details by ID**
3. **List active loans by member**
4. **List overdue loans**
5. **Get member details by email**
6. **List available copies of a book**
7. **Get loan history for a book copy**

### Secondary Access Patterns
8. List all employees
9. Get employee by ID
10. List all members
11. Search members by name

## DynamoDB Table Design

### Main Table: `lms-main`

#### Partition Key (PK) and Sort Key (SK) Strategy
```
PK Format: <ENTITY_TYPE>#<ID>
SK Format: <ENTITY_TYPE>#<SORT_VALUE>
```

#### Entity Types
- `BOOK#<book_id>`
- `COPY#<copy_id>`
- `MEMBER#<member_id>`
- `EMPLOYEE#<employee_id>`
- `LOAN#<loan_id>`

### Item Structures

#### Book Item
```json
{
  "PK": "BOOK#123",
  "SK": "BOOK#123",
  "EntityType": "BOOK",
  "BookId": "123",
  "Title": "El Progreso Del Peregrino",
  "Author": "John Bunyan",
  "ISBN": "1234567890123",
  "Publisher": "Publisher Name",
  "PublicationYear": 1678,
  "Genre": "Religious",
  "TotalCopies": 1,
  "AvailableCopies": 0,
  "CreatedAt": "2025-01-01T00:00:00Z",
  "UpdatedAt": "2025-01-01T00:00:00Z"
}
```

#### Book Copy Item
```json
{
  "PK": "BOOK#123",
  "SK": "COPY#456",
  "EntityType": "COPY",
  "CopyId": "456",
  "BookId": "123",
  "Status": "loaned",
  "CreatedAt": "2025-01-01T00:00:00Z",
  "UpdatedAt": "2025-01-01T00:00:00Z"
}
```

#### Member Item
```json
{
  "PK": "MEMBER#789",
  "SK": "MEMBER#789",
  "EntityType": "MEMBER",
  "MemberId": "789",
  "FirstName": "Galilea",
  "LastName": "Amador",
  "Email": "galilea.amador@example.com",
  "Phone": "+52-555-1234",
  "Address": "123 Main St, Mexico City",
  "Status": "active",
  "RegistrationDate": "2025-01-01",
  "CreatedAt": "2025-01-01T00:00:00Z",
  "UpdatedAt": "2025-01-01T00:00:00Z"
}
```

#### Employee Item
```json
{
  "PK": "EMPLOYEE#101",
  "SK": "EMPLOYEE#101",
  "EntityType": "EMPLOYEE",
  "EmployeeId": "101",
  "FirstName": "Jesús",
  "LastName": "Corona",
  "Position": "Librarian",
  "CreatedAt": "2025-01-01T00:00:00Z",
  "UpdatedAt": "2025-01-01T00:00:00Z"
}
```

#### Loan Item
```json
{
  "PK": "LOAN#555",
  "SK": "LOAN#555",
  "EntityType": "LOAN",
  "LoanId": "555",
  "CopyId": "456",
  "BookId": "123",
  "BookTitle": "El Progreso Del Peregrino",
  "MemberId": "789",
  "MemberName": "Galilea Amador",
  "EmployeeId": "101",
  "EmployeeName": "Jesús Corona",
  "LoanDate": "2025-11-23",
  "DueDate": "2025-12-21",
  "ActualReturnDate": null,
  "Status": "in_progress",
  "CreatedAt": "2025-01-01T00:00:00Z",
  "UpdatedAt": "2025-01-01T00:00:00Z"
}
```

## Global Secondary Indexes (GSIs)

### GSI1: Search by Title/Author (Autocomplete)
- **PK**: `GSI1PK` = `BOOK`
- **SK**: `GSI1SK` = `<Title>#<Author>`
- **Purpose**: Enable autocomplete search by title and author
- **Projection**: `ALL`

#### Example Items in GSI1
```json
{
  "GSI1PK": "BOOK",
  "GSI1SK": "El Progreso Del Peregrino#John Bunyan",
  "BookId": "123",
  "Title": "El Progreso Del Peregrino",
  "Author": "John Bunyan"
}
```

### GSI2: Member Loans and Email Lookup
- **PK**: `GSI2PK` = `MEMBER#<member_id>` or `EMAIL#<email>`
- **SK**: `GSI2SK` = `<loan_date>` or `MEMBER`
- **Purpose**: Get member by email, list loans by member
- **Projection**: `ALL`

#### Example Items in GSI2
```json
// Member lookup by email
{
  "GSI2PK": "EMAIL#galilea.amador@example.com",
  "GSI2SK": "MEMBER",
  "MemberId": "789",
  "FirstName": "Galilea",
  "LastName": "Amador"
}

// Loan by member
{
  "GSI2PK": "MEMBER#789",
  "GSI2SK": "2025-11-23",
  "LoanId": "555",
  "BookTitle": "El Progreso Del Peregrino",
  "Status": "in_progress"
}
```

### GSI3: Status-based Queries (Overdue, Active Loans)
- **PK**: `GSI3PK` = `STATUS#<status>`
- **SK**: `GSI3SK` = `<due_date>` or `<entity_id>`
- **Purpose**: Find overdue loans, active loans, available copies
- **Projection**: `ALL`

#### Example Items in GSI3
```json
// Overdue loans
{
  "GSI3PK": "STATUS#overdue",
  "GSI3SK": "2025-11-20",
  "LoanId": "555",
  "MemberId": "789",
  "BookTitle": "El Progreso Del Peregrino"
}

// Available copies
{
  "GSI3PK": "STATUS#available",
  "GSI3SK": "COPY#456",
  "CopyId": "456",
  "BookId": "123",
  "BookTitle": "El Progreso Del Peregrino"
}
```

## Query Patterns Implementation

### 1. Search Books (Autocomplete)
```python
# Query GSI1 with begins_with
response = dynamodb.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :pk AND begins_with(GSI1SK, :search)',
    ExpressionAttributeValues={
        ':pk': 'BOOK',
        ':search': 'El Progreso'
    },
    Limit=10
)
```

### 2. Get Member by Email
```python
response = dynamodb.query(
    IndexName='GSI2',
    KeyConditionExpression='GSI2PK = :email AND GSI2SK = :sk',
    ExpressionAttributeValues={
        ':email': 'EMAIL#galilea.amador@example.com',
        ':sk': 'MEMBER'
    }
)
```

### 3. List Active Loans by Member
```python
response = dynamodb.query(
    IndexName='GSI2',
    KeyConditionExpression='GSI2PK = :member',
    ExpressionAttributeValues={
        ':member': 'MEMBER#789'
    }
)
```

### 4. Find Overdue Loans
```python
response = dynamodb.query(
    IndexName='GSI3',
    KeyConditionExpression='GSI3PK = :status AND GSI3SK < :today',
    ExpressionAttributeValues={
        ':status': 'STATUS#in_progress',
        ':today': '2025-12-16'
    }
)
```

### 5. Get Book with Copies
```python
response = dynamodb.query(
    KeyConditionExpression='PK = :book',
    ExpressionAttributeValues={
        ':book': 'BOOK#123'
    }
)
```

## Cost Optimization Considerations

### Table Configuration
- **Billing Mode**: On-demand (perfect for low, unpredictable traffic)
- **Initial Data**: ~500 items (books, members, loans)
- **Growth Rate**: ~20 items/week
- **Peak Usage**: 1000 queries on Wed/Sun

### GSI Optimization
- **Minimal GSIs**: Only 3 GSIs for proven access patterns
- **Projection Type**: `ALL` for simplicity (small item sizes)
- **Sparse Indexes**: GSI2 and GSI3 use sparse indexing

### Estimated Monthly Cost
- **Table Storage**: ~$0.25/month (1GB)
- **On-demand Reads**: ~$1.25/month (1000 RCU)
- **On-demand Writes**: ~$1.25/month (1000 WCU)
- **GSI Storage**: ~$0.75/month (3 GSIs)
- **Total**: ~$3.50/month

## Migration Strategy

### Phase 1: Core Entities
1. Create main table with GSI1 (search)
2. Migrate books and copies
3. Implement search functionality

### Phase 2: Users and Loans
1. Add GSI2 and GSI3
2. Migrate members and employees
3. Migrate loan history

### Phase 3: Optimization
1. Monitor access patterns
2. Optimize GSI projections if needed
3. Add additional GSIs only if justified

## Data Seeding

The CSV data will be transformed and loaded using the following mapping:

```python
# CSV to DynamoDB transformation
csv_row = {
    "title": "El Progreso Del Peregrino",
    "author": "John Bunyan",
    "status": "Prestado",
    "employee": "Jesús Corona",
    "member": "Galilea Amador",
    "loan_date": "2025-11-23",
    "due_date": "2025-12-21"
}

# Creates: Book, Copy, Member, Employee, Loan items
```

This design provides efficient access patterns while maintaining cost optimization for the expected usage profile.