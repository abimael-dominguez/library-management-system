# SQL to NoSQL Mapping Documentation

## Overview
This document explains the rationale and methodology for mapping the PostgreSQL relational schema to DynamoDB NoSQL design for the Library Management System.

## Relational vs NoSQL Design Philosophy

### PostgreSQL (Relational) Approach
- **Normalization**: Separate tables for each entity to avoid data duplication
- **Relationships**: Foreign keys enforce referential integrity
- **Queries**: JOINs combine data from multiple tables
- **ACID**: Strong consistency and transactions

### DynamoDB (NoSQL) Approach
- **Denormalization**: Store related data together to minimize queries
- **Single Table**: One table with multiple entity types
- **Access Patterns**: Design driven by how data will be queried
- **Eventually Consistent**: Optimized for scale and performance

## Entity Mapping

### 1. Book Entity

#### PostgreSQL Schema
```sql
CREATE TABLE book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(17) UNIQUE,
    publisher VARCHAR(255),
    publication_year INTEGER,
    genre VARCHAR(100)
);
```

#### DynamoDB Item
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
  "GSI1PK": "BOOK",
  "GSI1SK": "El Progreso Del Peregrino#John Bunyan"
}
```

**Key Changes:**
- Added `TotalCopies` and `AvailableCopies` (denormalized from book_copy count)
- Added GSI attributes for search functionality
- Composite sort key in GSI1 enables title/author search

### 2. Book Copy Entity

#### PostgreSQL Schema
```sql
CREATE TABLE book_copy (
    book_copy_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES book(book_id),
    status VARCHAR(20) NOT NULL
);
```

#### DynamoDB Item
```json
{
  "PK": "BOOK#123",
  "SK": "COPY#456",
  "EntityType": "COPY",
  "CopyId": "456",
  "BookId": "123",
  "Status": "loaned",
  "GSI3PK": "STATUS#loaned",
  "GSI3SK": "COPY#456"
}
```

**Key Changes:**
- Uses same PK as book (enables single query for book + copies)
- Added GSI3 for status-based queries (find available copies)
- Removed foreign key constraint (handled in application logic)

### 3. Member Entity

#### PostgreSQL Schema
```sql
CREATE TABLE member (
    member_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(254) UNIQUE NOT NULL,
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL
);
```

#### DynamoDB Item
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
  "GSI2PK": "EMAIL#galilea.amador@example.com",
  "GSI2SK": "MEMBER"
}
```

**Key Changes:**
- Added GSI2 for email-based lookup (replaces UNIQUE constraint)
- Email becomes part of GSI key structure
- Status values mapped to English

### 4. Employee Entity

#### PostgreSQL Schema
```sql
CREATE TABLE employee (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL
);
```

#### DynamoDB Item
```json
{
  "PK": "EMPLOYEE#101",
  "SK": "EMPLOYEE#101",
  "EntityType": "EMPLOYEE",
  "EmployeeId": "101",
  "FirstName": "Jesús",
  "LastName": "Corona",
  "Position": "Librarian"
}
```

**Key Changes:**
- Minimal changes (simple entity)
- No additional GSI needed (small dataset)

### 5. Loan Entity

#### PostgreSQL Schema
```sql
CREATE TABLE loan (
    loan_id SERIAL PRIMARY KEY,
    book_copy_id INTEGER NOT NULL REFERENCES book_copy(book_copy_id),
    member_id INTEGER NOT NULL REFERENCES member(member_id),
    employee_id INTEGER REFERENCES employee(employee_id),
    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    actual_return_date DATE,
    status VARCHAR(20) NOT NULL
);
```

#### DynamoDB Item
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
  "GSI2PK": "MEMBER#789",
  "GSI2SK": "2025-11-23",
  "GSI3PK": "STATUS#in_progress",
  "GSI3SK": "2025-12-21"
}
```

**Key Changes:**
- **Heavy Denormalization**: Added `BookTitle`, `MemberName`, `EmployeeName`
- **Dual GSI Usage**: GSI2 for member loans, GSI3 for status queries
- **Removed Foreign Keys**: Relationships maintained through IDs

## Access Pattern Comparison

### 1. Search Books by Title

#### PostgreSQL
```sql
SELECT * FROM book 
WHERE title ILIKE '%progreso%' 
ORDER BY title 
LIMIT 10;
```

#### DynamoDB
```python
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

**Trade-offs:**
- ✅ DynamoDB: Predictable performance, no full table scan
- ❌ DynamoDB: Less flexible search (prefix-based only)

### 2. Get Member's Active Loans

#### PostgreSQL
```sql
SELECT l.*, b.title, b.author 
FROM loan l
JOIN book_copy bc ON l.book_copy_id = bc.book_copy_id
JOIN book b ON bc.book_id = b.book_id
WHERE l.member_id = 789 AND l.status = 'in_progress';
```

#### DynamoDB
```python
response = dynamodb.query(
    IndexName='GSI2',
    KeyConditionExpression='GSI2PK = :member',
    FilterExpression='#status = :status',
    ExpressionAttributeValues={
        ':member': 'MEMBER#789',
        ':status': 'in_progress'
    }
)
```

**Trade-offs:**
- ✅ DynamoDB: Single query, no JOINs, includes book title
- ✅ DynamoDB: Consistent performance regardless of data size
- ❌ DynamoDB: Uses FilterExpression (less efficient than KeyCondition)

### 3. Find Overdue Loans

#### PostgreSQL
```sql
SELECT l.*, m.first_name, m.last_name, b.title
FROM loan l
JOIN member m ON l.member_id = m.member_id
JOIN book_copy bc ON l.book_copy_id = bc.book_copy_id
JOIN book b ON bc.book_id = b.book_id
WHERE l.status = 'in_progress' 
AND l.due_date < CURRENT_DATE;
```

#### DynamoDB
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

**Trade-offs:**
- ✅ DynamoDB: Single query, no JOINs, all data included
- ✅ DynamoDB: Efficient range query on due date
- ✅ DynamoDB: Scales linearly with overdue loans, not total loans

## Design Decisions Rationale

### 1. Single Table Design
**Decision**: Use one table with multiple entity types
**Rationale**: 
- Reduces cross-table queries
- Better performance for related data access
- Cost-effective for small to medium datasets
- Aligns with DynamoDB best practices

### 2. Denormalization Strategy
**Decision**: Store book titles, member names in loan records
**Rationale**:
- Eliminates JOINs for common queries
- Improves read performance
- Acceptable data duplication for read-heavy workload
- Names/titles change infrequently

### 3. GSI Design
**Decision**: Three GSIs for specific access patterns
**Rationale**:
- GSI1: Search functionality (critical for UX)
- GSI2: Member-centric queries (loans, email lookup)
- GSI3: Status-based operations (overdue, available)
- Minimal GSIs to control costs

### 4. Composite Keys
**Decision**: Use meaningful composite keys (e.g., `BOOK#123`)
**Rationale**:
- Self-documenting
- Enables hierarchical queries
- Supports single-table design
- Easy debugging and maintenance

## Performance Implications

### Read Performance
- **PostgreSQL**: O(log n) with proper indexes, but JOINs add overhead
- **DynamoDB**: O(1) for single item, O(log n) for range queries, no JOINs

### Write Performance
- **PostgreSQL**: Foreign key validation overhead, transaction locks
- **DynamoDB**: Direct writes, eventual consistency, no referential integrity checks

### Scalability
- **PostgreSQL**: Vertical scaling, complex sharding for horizontal scale
- **DynamoDB**: Automatic horizontal scaling, predictable performance

## Cost Analysis

### Storage Costs
- **PostgreSQL**: Normalized data = less storage
- **DynamoDB**: Denormalized data = ~30% more storage, but still minimal for LMS

### Query Costs
- **PostgreSQL**: Fixed cost regardless of query complexity
- **DynamoDB**: Pay per request, but predictable costs

### Operational Costs
- **PostgreSQL**: Server management, backups, maintenance
- **DynamoDB**: Fully managed, automatic scaling

## Migration Considerations

### Data Integrity
- **Lost**: Foreign key constraints, ACID transactions
- **Gained**: Application-level validation, eventual consistency benefits

### Query Flexibility
- **Lost**: Ad-hoc SQL queries, complex JOINs
- **Gained**: Predictable performance, better caching

### Development Complexity
- **Added**: GSI design, access pattern planning
- **Reduced**: No schema migrations, automatic scaling

This mapping provides a foundation for efficient library operations while maintaining cost optimization and scalability for the expected usage patterns.