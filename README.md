# Library Management System

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-local--first-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-336791.svg)](https://www.postgresql.org/)

Local-first migration of the library backend from the old serverless DynamoDB design to a transactional relational design using FastAPI and SQLAlchemy.

This phase is focused on manual local testing only. Cloud deployment comes later.

## Current Architecture

### Local phase
- Frontend: static files in `frontend/src`
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

### 3. Initialize demo data

```bash
python scripts/seed_local_db.py
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
