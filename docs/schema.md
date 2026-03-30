# Database Schema

This document describes the logical relational schema for the Library Management System.

It is written to stay useful across both environments:

- local development currently uses SQLite through SQLAlchemy
- production is expected to use PostgreSQL later

The domain model should remain the same across both databases. Environment-specific details, indexes, and migration concerns are noted separately.

## Source Of Truth

The current implementation source of truth is:

- `src/infrastructure/models.py` for the active SQLAlchemy schema

Important note:

- `create_tables.sql` is not fully aligned with the current SQLAlchemy models. In particular, it still uses `SERIAL` integer IDs, while the application currently uses string-based application-generated IDs such as `String(36)` and `String(64)`.

## Logical Schema Overview

The system is centered around five relational tables:

- `book`: metadata for a title
- `book_copy`: a physical inventory copy of a book
- `member`: a library patron
- `employee`: a staff member
- `loan`: a borrowing transaction for a specific copy

### Design intention

- A `book` represents the title-level record
- A `book_copy` represents each physical copy that can be loaned
- A `loan` always belongs to one specific copy, not just to a title
- All writes go through the backend application layer
- Loan and return operations are enforced as backend transactions

## Table Definitions

### 1. `book` (Metadata For The Title)

This table stores information about a book title, not the individual physical copies.

| Field Name | Description | Data Type / Notes |
|---|---|---|
| `book_id` | Primary Key (PK) | `String(36)` application-generated ID |
| `title` | The name of the book | `String(255)`, indexed, required |
| `author` | The main author | `String(255)`, indexed, required |
| `isbn` | International Standard Book Number | `String(17)`, unique, optional |
| `publisher` | The publishing house | `String(255)`, optional |
| `publication_year` | The year the book was published | `Integer`, optional |
| `genre` | The book genre | `String(100)`, optional |
| `pages` | Number of pages | `Integer`, optional |
| `max_loan_weeks` | Default number of allowed loan weeks | `Integer`, required, default `3` |
| `total_copies` | Total registered copies for the title | `Integer`, required, default `1` |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

Relationship notes:

- One `book` can have many `book_copy` records
- Deleting a `book` cascades to its copies in the current implementation
- The API may expose computed availability fields for a book, but those are not stored directly in this table

### 2. `book_copy` (Physical Inventory Item)

This table tracks each physical copy of a book.

| Field Name | Description | Data Type / Notes |
|---|---|---|
| `book_copy_id` | Primary Key (PK) | `String(64)` application-generated copy ID |
| `book_id` | Foreign Key (FK) | References `book.book_id`, required, indexed, `ON DELETE CASCADE` |
| `status` | Current physical state and availability | `String(20)`, required, default `available` |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

Allowed `status` values:

- `available`
- `loaned`
- `damaged`
- `lost`

### 3. `member` (Library Patrons)

Stores information about borrowers.

| Field Name | Description | Data Type / Notes |
|---|---|---|
| `member_id` | Primary Key (PK) | `String(36)` application-generated ID |
| `first_name` | Member first name | `String(100)`, indexed, required |
| `last_name` | Member last name | `String(100)`, indexed, required |
| `address` | Member mailing address | `String(255)`, optional |
| `phone` | Contact phone number | `String(20)`, optional |
| `email` | Member email address | `String(254)`, unique, required |
| `registration_date` | Date the member joined | `Date`, required, default current date |
| `status` | Member account status | `String(20)`, required, default `active` |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

Allowed `status` values:

- `active`
- `inactive`
- `suspended`

### 4. `employee` (Library Staff)

Stores staff members involved in loan processing.

| Field Name | Description | Data Type / Notes |
|---|---|---|
| `employee_id` | Primary Key (PK) | `String(36)` application-generated ID |
| `first_name` | Employee first name | `String(100)`, required |
| `last_name` | Employee last name | `String(100)`, required |
| `position` | Employee job title | `String(100)`, required |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

### 5. `loan` (Transaction Record)

Records each borrowing transaction for a specific physical copy.

| Field Name | Description | Data Type / Notes |
|---|---|---|
| `loan_id` | Primary Key (PK) | `String(36)` application-generated ID |
| `book_copy_id` | Foreign Key (FK) | References `book_copy.book_copy_id`, required, indexed, `ON DELETE CASCADE` |
| `member_id` | Foreign Key (FK) | References `member.member_id`, required, indexed, `ON DELETE CASCADE` |
| `employee_id` | Foreign Key (FK) | References `employee.employee_id`, optional, `ON DELETE SET NULL` |
| `loan_date` | Date the book was borrowed | `Date`, required |
| `due_date` | Estimated return date | `Date`, required |
| `actual_return_date` | Real return date | `Date`, optional |
| `status` | Current transaction state | `String(20)`, required, default `in_progress` |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

Allowed `status` values:

- `in_progress`
- `returned`
- `overdue`

## Constraints And Business Rules

- `loan.due_date >= loan.loan_date`
- `loan.actual_return_date` must be null or on/after `loan.loan_date`
- Only one active loan per copy is allowed
- A returned copy can later be loaned again
- A `loan` always points to a specific `book_copy`, not just to a `book`
- The API exposes `available_copies` and `first_available_copy_id` as computed response fields, but those are not stored directly in the `book` table

## Current Implementation Notes

The current SQLAlchemy implementation in `src/infrastructure/models.py` adds the following important details:

- Timestamp columns are managed through a shared mixin
- Status fields are enforced through `CHECK` constraints
- The one-active-loan-per-copy rule is enforced through the filtered unique index `ix_loan_one_active_copy`
- That filtered unique index is defined for both SQLite and PostgreSQL in SQLAlchemy
- Primary keys are application-generated strings, not auto-increment integers

## SQLite And PostgreSQL Notes

The logical schema is meant to stay the same, but some implementation behavior matters when moving from SQLite to PostgreSQL.

### Stable across both databases

- Table structure
- Relationships
- Status sets
- Core business constraints
- One active loan per copy rule

### Things to watch during PostgreSQL production migration

- Keep the SQLAlchemy models as the schema source of truth, or introduce managed migrations with Alembic before relying on handwritten SQL
- Make sure indexes and filtered unique constraints are created consistently in production
- Confirm timestamp behavior and timezone expectations explicitly
- Preserve string-based IDs unless there is a deliberate migration plan to another identifier strategy
- Treat `create_tables.sql` as outdated until it is rewritten to match the application schema

## Recommendation

For current work and future production migration, use this document as the logical schema reference and treat `src/infrastructure/models.py` as the implementation reference.

If PostgreSQL becomes the production target, the next useful step will be to align `create_tables.sql` or replace it with proper migrations so the documented schema, ORM schema, and deployment schema all match.
