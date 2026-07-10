# Library Management System

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-local--first-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-336791.svg)](https://www.postgresql.org/)

Local-first library management system built with FastAPI, SQLAlchemy, and a static frontend. The current phase is focused on local development and manual testing with SQLite, while keeping the application ready to switch to PostgreSQL later through configuration.

## Table of Contents

- [Overview](#overview)
- [Current Features](#current-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Prerequisites](#prerequisites)
- [Recommended Docker Workflow](#recommended-docker-workflow)
- [Operational Command Reference](#operational-command-reference)
  - [Quick lookup](#quick-lookup)
  - [Daily workflow](#daily-workflow)
  - [Logs](#logs)
  - [Container status](#container-status)
  - [Builds](#builds)
  - [Data import](#data-import)
  - [Tests](#tests)
- [Local Development Without Docker](#local-development-without-docker)
- [Common API Checks](#common-api-checks)
- [Test Commands](#test-commands)
- [Environment Variables](#environment-variables)
- [API Surface](#api-surface)
- [Manual Smoke Test](#manual-smoke-test)
- [Example API Requests](#example-api-requests)
- [Notes](#notes)
- [Future Direction](#future-direction)

## Overview

- Backend API: FastAPI application in `src/`
- Frontend: static app served from `frontend/src/`
- Local database: SQLite at `data/local/library.db`
- Seed source: CSV import or demo data
- Future-ready: `DATABASE_URL` can be changed later to PostgreSQL without changing the API contract

## Current Features

- Health check and import summary
- Book catalog listing, search, autocomplete, and creation
- Member registration and listing
- Employee registration and listing
- Loan creation, listing, lookup, and return flow
- Transactional backend handling for loan and return operations

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite for local development
- PostgreSQL-ready configuration
- Static frontend served with Python HTTP server or Docker

## Project Structure

```text
src/
  application/
    dto/
    use_cases/
  domain/
    entities/
    repositories/
    exceptions.py
  infrastructure/
    api.py
    database.py
    models.py
    repositories/
    seed.py
    settings.py
  main.py

frontend/src/
  application/
  domain/
  infrastructure/
  ui/
  app.js
  index.html
  styles.css

scripts/
  seed_local_db.py
  test.sh

tests/
  unit/
  functional/
```

## Documentation

- Database schema: [docs/schema.md](docs/schema.md)

## Prerequisites

- Python 3.11+
- Docker and Docker Compose for the containerized workflow

## Recommended Docker Workflow

Use this workflow for day-to-day local development. It rebuilds the API image when needed, starts the API and frontend in the background, and keeps the local database refresh explicit.

### 1. Create the local environment file

```bash
cp .env.example .env
```

### 2. Start or refresh the API and frontend

```bash
docker compose up -d --build api frontend --remove-orphans
```

The `--build` flag is intentionally part of the recommended command. It prevents stale API images after changes to files copied into the Docker image, such as `scripts/`, `requirements.txt`, or `Dockerfile`.

The frontend is currently a static app mounted from `frontend/src`, so it does not need a separate frontend build. After frontend changes, refresh `http://localhost:8080`.

### 3. Seed the local database

```bash
docker compose run --rm api python scripts/seed_local_db.py
```

By default, this imports `data/library-cbg-clean.csv`, recreates the local library data, and writes the import summary.

The seed script is intentionally explicit and local-only: it refuses to run outside `APP_ENV=local` or `APP_ENV=test` unless `--force` is passed. After seeding, review `data/local/last_seed_summary.json` or `GET /import-summary` for skipped rows and data-quality warnings.

### 4. Open the application

- Frontend: [http://localhost:8080](http://localhost:8080)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 5. Stop the containers

```bash
docker compose down --remove-orphans
```

## Operational Command Reference

These are the most useful commands for local development. Prefer the Docker workflow unless you are specifically debugging Python environment behavior outside containers.

### Quick lookup

| Task | Command |
| --- | --- |
| Create `.env` | `cp .env.example .env` |
| Start or refresh app | `docker compose up -d --build api frontend --remove-orphans` |
| Seed local database | `docker compose run --rm api python scripts/seed_local_db.py` |
| Follow API and frontend logs | `docker compose logs -f --tail=100 api frontend` |
| Show container status | `docker compose ps` |
| Restart services | `docker compose restart api frontend` |
| Stop services | `docker compose down --remove-orphans` |
| Run tests | `docker compose run --rm test` |

### Daily workflow

Start or refresh the app:

```bash
docker compose up -d --build api frontend --remove-orphans
```

Rebuild the local SQLite data from the CSV:

```bash
docker compose run --rm api python scripts/seed_local_db.py
```

Open the app:

- Frontend: [http://localhost:8080](http://localhost:8080)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

Stop the app:

```bash
docker compose down --remove-orphans
```

### Logs

Follow API and frontend logs together:

```bash
docker compose logs -f --tail=100 api frontend
```

Follow only API logs:

```bash
docker compose logs -f --tail=100 api
```

Follow only frontend logs:

```bash
docker compose logs -f --tail=100 frontend
```

Show recent logs without following:

```bash
docker compose logs --tail=100 api frontend
```

Press `Ctrl+C` to exit log following. This only closes the log viewer; it does not stop the containers.

### Container status

List running project containers:

```bash
docker compose ps
```

Restart the running services:

```bash
docker compose restart api frontend
```

Stop and remove project containers:

```bash
docker compose down --remove-orphans
```

### Builds

Start services and rebuild the API image if needed:

```bash
docker compose up -d --build api frontend --remove-orphans
```

Rebuild only the API image:

```bash
docker compose build api
```

Use this when you want to rebuild without starting or recreating containers. For normal local work, prefer `docker compose up -d --build api frontend --remove-orphans`.

Use `--build` after changes to files copied into the API image, especially:

- `scripts/`
- `requirements.txt`
- `Dockerfile`
- `pytest.ini`

Changes inside `src/` are normally picked up by the API reload process, but the recommended start command includes `--build` to avoid stale image confusion.

The frontend does not have a separate build step right now. Docker serves the static files mounted from `frontend/src`, so frontend changes usually only require a browser refresh.

### Data import

```bash
docker compose run --rm api python scripts/seed_local_db.py
```

Optional seed variants:

```bash
docker compose run --rm api python scripts/seed_local_db.py --csv data/library-cbg-clean.csv
docker compose run --rm api python scripts/seed_local_db.py --demo
docker compose run --rm api python scripts/seed_local_db.py --no-rebuild-schema
```

Review the last import summary:

```bash
curl http://localhost:8000/import-summary
```

### Tests

```bash
docker compose run --rm test
```

The helper script runs the same Docker test service:

```bash
./scripts/test.sh
```

## Local Development Without Docker

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
export APP_ENV=local
export DATABASE_URL=sqlite:///./data/local/library.db
export AUTO_CREATE_DB=true
export CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

### 3. Seed the local database

```bash
python scripts/seed_local_db.py
```

Optional variants:

```bash
python scripts/seed_local_db.py --csv data/library-cbg-clean.csv
python scripts/seed_local_db.py --demo
python scripts/seed_local_db.py --no-rebuild-schema
```

### 4. Start the backend

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start the frontend in another terminal

```bash
python3 -m http.server 8080 --directory frontend/src
```

## Common API Checks

### Health check

```bash
curl http://localhost:8000/health
```

### Import summary

```bash
curl http://localhost:8000/import-summary
```

### Search books

```bash
curl "http://localhost:8000/search?q=gracia&limit=5" | python3 -m json.tool
```

### List open loans

```bash
curl "http://localhost:8000/loans?limit=5" | python3 -m json.tool
```

## Test Commands

### Docker

```bash
docker compose run --rm test
```

### Local virtual environment

```bash
pytest tests/unit tests/functional
```

## Environment Variables

`.env.example` contains the default local configuration:

```env
APP_ENV=local
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=sqlite:///./data/local/library.db
AUTO_CREATE_DB=true
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

Key behavior:

- `APP_ENV=local` enables the local development profile
- `DATABASE_URL` points to SQLite locally and can later point to PostgreSQL
- `AUTO_CREATE_DB=true` creates the schema automatically on startup
- `CORS_ORIGINS` allows the local frontend to call the API
- Seeding is not automatic on API startup; run `scripts/seed_local_db.py` explicitly for local data resets

## API Surface

### Utility endpoints

- `GET /health`
- `GET /import-summary`

### Books

- `GET /books`
- `POST /books`
- `GET /books/{book_id}`
- `GET /search?q=...`
- `GET /autocomplete?q=...&type=book`

### Members

- `GET /members`
- `POST /members`
- `GET /autocomplete?q=...&type=member`

### Employees

- `GET /employees`
- `POST /employees`

### Loans

- `GET /loans`
- `POST /loans`
- `GET /loans/{loan_id}`
- `PUT /loans/{loan_id}/return`

## Manual Smoke Test

### Frontend

1. Open `http://localhost:8080`
2. Confirm the dashboard loads books and summary counts
3. Create a member
4. Create an employee
5. Create a loan
6. Return the loan
7. Refresh the page and confirm the returned state persists

### Backend

1. Call `GET /health`
2. Call `GET /books`, `GET /members`, `GET /employees`, `GET /loans`, and `GET /import-summary`
3. Create a member with `POST /members`
4. Create an employee with `POST /employees`
5. Create a loan with `POST /loans`
6. Return the loan with `PUT /loans/{loan_id}/return`
7. Reload the loan with `GET /loans/{loan_id}` and confirm its status is `returned`

## Example API Requests

### Create a member

```bash
curl -X POST http://localhost:8000/members \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Elena",
    "last_name": "Ruiz",
    "email": "elena.ruiz@example.com"
  }'
```

### Create an employee

```bash
curl -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marco",
    "last_name": "Diaz",
    "position": "Librarian"
  }'
```

### Create a book

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Domain-Driven Design",
    "author": "Eric Evans",
    "total_copies": 2
  }'
```

### List books

```bash
curl http://localhost:8000/books
```

### Create a loan

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

### Return a loan

```bash
curl -X PUT http://localhost:8000/loans/REPLACE_WITH_LOAN_ID/return \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Notes

- The frontend never writes directly to the database
- All writes go through the FastAPI backend
- Loan and return operations are handled as backend transactions
- The current importer treats the CSV as the temporary source of truth for local rebuilds
- Rows marked as loaned in the source data create active loans during import

## Future Direction

This local structure is designed to support a later cloud deployment phase with:

- PostgreSQL instead of SQLite through `DATABASE_URL`
- Containerized backend deployment
- Static frontend hosting behind a CDN
- Explicit environment-based configuration rather than code changes
