# Library Management System

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-local--first-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-336791.svg)](https://www.postgresql.org/)

Local-first migration of the library backend from the old serverless DynamoDB design to a transactional relational design using FastAPI and SQLAlchemy.

This phase is focused on manual local testing only. Cloud deployment comes later.

## Current Architecture

### Local phase
- Frontend: static files in `frontend/src`, organized in `application`, `domain`, `infrastructure`, and `ui`
- Backend API: FastAPI app assembled from `src/application`, `src/domain`, and `src/infrastructure`
- Local database: SQLite file at `data/local/library.db`
- Optional later database: PostgreSQL by changing only `DATABASE_URL`

### Important principle
- The frontend never writes directly to the database.
- All writes go through the FastAPI backend.
- Loan and return operations are handled as backend transactions.

## What Works In This Phase

- `GET /health`
- `GET /books`
- `POST /books`
- `GET /books/{book_id}`
- `GET /search?q=...`
- `GET /autocomplete?q=...&type=member`
- `GET /members`
- `POST /members`
- `GET /employees`
- `POST /employees`
- `GET /loans`
- `POST /loans`
- `GET /loans/{loan_id}`
- `PUT /loans/{loan_id}/return`

## Database Schema Definition

This section reflects the current relational schema implemented in [src/infrastructure/models.py](/Users/mi20429/Documents/code/explorations/tecgurus_courses/library-management-system/src/infrastructure/models.py).

### 1. `book` (Metadata for the Title)

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

### 2. `book_copy` (Physical Inventory Item)

This table tracks each physical copy of a book.

| Field Name | Description | Data Type / Notes |
|---|---|---|
| `book_copy_id` | Primary Key (PK) | `String(64)` application-generated copy ID |
| `book_id` | Foreign Key (FK) | References `book.book_id`, required, `ON DELETE CASCADE` |
| `status` | Current physical state and availability | `String(20)`, required, choices: `available`, `loaned`, `damaged`, `lost` |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

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
| `status` | Member account status | `String(20)`, required, choices: `active`, `inactive`, `suspended` |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

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
| `book_copy_id` | Foreign Key (FK) | References `book_copy.book_copy_id`, required, `ON DELETE CASCADE` |
| `member_id` | Foreign Key (FK) | References `member.member_id`, required, `ON DELETE CASCADE` |
| `employee_id` | Foreign Key (FK) | References `employee.employee_id`, optional, `ON DELETE SET NULL` |
| `loan_date` | Date the book was borrowed | `Date`, required |
| `due_date` | Estimated return date | `Date`, required |
| `actual_return_date` | Real return date | `Date`, optional |
| `status` | Current transaction state | `String(20)`, required, choices: `in_progress`, `returned`, `overdue` |
| `created_at` | Record creation timestamp | `DateTime`, auto-managed |
| `updated_at` | Record update timestamp | `DateTime`, auto-managed |

### Constraints and Notes

- `loan.due_date >= loan.loan_date`
- `loan.actual_return_date` must be null or on/after `loan.loan_date`
- Only one active loan per copy is allowed through a unique filtered index on `loan.book_copy_id` where status is `in_progress`
- The API exposes `available_copies` and `first_available_copy_id` as computed response fields, but those are not stored directly in the `book` table

## Local Run With Python

These commands work well in `bash` on macOS.

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Set local environment variables

```bash
cp .env.example .env
export APP_ENV=local
export DATABASE_URL=sqlite:///./data/local/library.db
export AUTO_CREATE_DB=true
export CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

### 3. Synchronize the database from the spreadsheet CSV

```bash
python scripts/seed_local_db.py
```

By default this reads `data/library-cbg-clean.csv`, resets the local library tables, and rebuilds the database from the spreadsheet export.

If you want to import a different CSV file:

```bash
python scripts/seed_local_db.py --csv data/library-cbg-clean.csv
```

If you want the small demo dataset instead:

```bash
python scripts/seed_local_db.py --demo
```

### 4. Start the API

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start the frontend in another terminal

```bash
python3 -m http.server 8080 --directory frontend/src
```

### 6. Open the app

- Frontend: [http://localhost:8080](http://localhost:8080)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

## Local Run With Docker

### Start API and frontend

```bash
docker compose up --build api frontend
```

### Run tests in Docker

```bash
./scripts/test.sh
```

### Stop local containers

```bash
docker compose down
```

## Manual Smoke Test Flow

### Option 1: Use the frontend
1. Open `http://localhost:8080`
2. Verify books load automatically
3. Add a book
4. Create a member
5. Create an employee
6. Create a loan from the UI
7. Return the loan from the UI

### Option 2: Use curl

Create a member:

```bash
curl -X POST http://localhost:8000/members \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Elena",
    "last_name": "Ruiz",
    "email": "elena.ruiz@example.com"
  }'
```

Create an employee:

```bash
curl -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marco",
    "last_name": "Diaz",
    "position": "Librarian"
  }'
```

Create a book:

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Domain-Driven Design",
    "author": "Eric Evans",
    "total_copies": 2
  }'
```

List books:

```bash
curl http://localhost:8000/books
```

Create a loan:

```bash
curl -X POST http://localhost:8000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "book_copy_id": "REPLACE_WITH_COPY_ID",
    "member_id": "REPLACE_WITH_MEMBER_ID",
    "employee_id": "REPLACE_WITH_EMPLOYEE_ID",
    "loan_date": "2026-03-18",
    "due_date": "2026-04-08"
  }'
```

Return a loan:

```bash
curl -X PUT http://localhost:8000/loans/REPLACE_WITH_LOAN_ID/return \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Test Strategy In This Phase

- Unit tests: service and schema behavior
- Functional tests: API endpoints with isolated SQLite
- Frontend: manual browser verification against localhost API

### Recommended Runtime Smoke Tests

Run these after the API and frontend are both up locally.

#### Frontend smoke test
1. Open `http://localhost:8080`
2. Verify the burger menu opens and shows `Home`, `Members`, and `Employees`
3. Verify the home dashboard loads counts for books, active loans, overdue loans, and members
4. Click `Loans` and confirm the main list switches from books to active loans
5. Click `Overdue` and confirm the main list switches to overdue loans
6. Click `Catalog` and confirm the main list switches back to books
7. Open `New Loan`, select a book, member, and employee, then create the loan
8. Confirm the new loan appears in the `Loans` list
9. Use `Register return` from the active loan list and confirm the loan disappears from active loans
10. Refresh the browser and confirm the returned loan state is still correct
11. Open `Members` from the side menu and create a member
12. Open `Employees` from the side menu and create an employee
13. Toggle theme and confirm the icon and colors update correctly

#### Backend smoke test
1. Call `GET /health` and confirm `{"status":"ok"}` is returned
2. Call `GET /books`, `GET /members`, `GET /employees`, `GET /loans`, and `GET /import-summary`
3. Create a member with `POST /members`
4. Create an employee with `POST /employees`
5. Create a loan with `POST /loans`
6. Return the loan with `PUT /loans/{loan_id}/return`
7. Reload the same loan with `GET /loans/{loan_id}` and confirm `status=returned`
8. Create a second loan for the same copy and confirm it succeeds after the return

Run locally without Docker:

```bash
pytest tests/unit tests/functional
```

Run with Docker:

```bash
docker compose run --rm test
```

## Environment Variables

These are the key variables that make the local and future cloud setup clean.

| Variable | Local Value | Later Cloud Value |
|---|---|---|
| `APP_ENV` | `local` | `dev` or `prod` |
| `DATABASE_URL` | `sqlite:///./data/local/library.db` | `postgresql+psycopg://...` |
| `AUTO_CREATE_DB` | `true` | usually `false` once migrations are managed |
| `CORS_ORIGINS` | local frontend URLs | CloudFront/custom domain URLs |

This is the main professional switch point:
- local uses SQLite
- cloud will use PostgreSQL
- the application code keeps the same API contract

## Project Structure

```text
src/application/
  dto/
  use_cases/

src/domain/
  entities/
  repositories/
  exceptions.py

src/infrastructure/
  api.py
  database.py
  models.py
  repositories/
  seed.py

src/main.py

frontend/src/
  application/
    services/
    state/
  domain/
  infrastructure/
    api/
    storage/
  ui/
  index.html
  app.js
  styles.css

tests/
  unit/
  functional/
```

## Notes For Phase 2

Not implemented yet, but this local structure is already prepared for:
- CloudFormation-based deployment
- containerized FastAPI on ECS/Fargate
- S3 + CloudFront for the frontend
- PostgreSQL outside local SQLite by changing `DATABASE_URL`

When we start phase 2, the database being remote instead of local will be indicated explicitly by environment variables and stack parameters, not hidden in code.

## Legacy Serverless Reference

The previous serverless code was moved out of the active source tree to keep the repo cleaner:

- `tmp/serverless-legacy/`
- `tmp/refactor-backup/`

If we need the original AWS Lambda and DynamoDB implementation later, we can also consult the `serverless-project-tecgurus` branch.

## Spreadsheet Sync Notes

The current importer assumes the CSV is the temporary source of truth while the library still works with the spreadsheet.

- Every run of `python scripts/seed_local_db.py` rebuilds the local data from the CSV.
- Rows marked as `Prestado` or `Prestamo` create active loans.
- Rows marked as `Entregado` create books and copies but no active loan.
- If a loaned row is missing member or date data, the importer fills sensible placeholders and reports warnings in the summary output.
