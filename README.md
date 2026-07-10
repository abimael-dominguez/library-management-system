# Library Management System

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/database-PostgreSQL%20local-336791.svg)](https://www.postgresql.org/)
[![Smoke Tests](https://img.shields.io/badge/smoke-Playwright-45ba4b.svg)](https://playwright.dev/)

Operational library circulation app built with FastAPI, SQLAlchemy, PostgreSQL, and a static HTML/CSS/JS frontend. The local workflow is intentionally close to the future Supabase/PostgreSQL path: schema changes go through Alembic migrations, data import is explicit, and the frontend talks only to the API.

## Table Of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Daily Commands](#daily-commands)
- [Database And Migrations](#database-and-migrations)
- [Data Import](#data-import)
- [Tests](#tests)
- [Logs And Debugging](#logs-and-debugging)
- [API Checks](#api-checks)
- [Environment Variables](#environment-variables)
- [Local Without Docker](#local-without-docker)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Future Direction](#future-direction)

## Overview

- Backend API: FastAPI app in `src/`
- Frontend: static operational workspace in `frontend/src/`
- Local DB: PostgreSQL service `db`, exposed on host port `5433` by default
- Migrations: Alembic baseline in `alembic/`
- Seed source: `data/library-cbg-clean.csv`
- Backend tests: pytest inside Docker against PostgreSQL `lms_test`
- Frontend smoke tests: Playwright inside Docker

SQLite still works as a manual fallback, but it is no longer the recommended development path.

## Architecture

- `frontend/src/ui/`: workspace navigation, renderers, modals, form payload helpers
- `frontend/src/application/`: frontend service/state orchestration
- `frontend/src/infrastructure/`: API client and browser preferences
- `src/domain/`: entities, repository contracts, domain exceptions
- `src/application/`: use cases and DTOs
- `src/infrastructure/`: FastAPI routes, SQLAlchemy adapters, config, seed/import

The frontend renders, pre-fills, and requests actions. Business rules remain in backend use cases and database constraints.

## Prerequisites

- Docker and Docker Compose
- Optional for non-Docker work: Python 3.11+ and Node 20+

## Quick Start

Create a local env file:

```bash
cp .env.example .env
```

Start or refresh the app stack:

```bash
docker compose up -d --build db api frontend --remove-orphans
```

Apply database migrations:

```bash
docker compose run --rm api alembic upgrade head
```

Seed local data:

```bash
docker compose run --rm api python scripts/seed_local_db.py
```

Open:

- Frontend: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

Stop:

```bash
docker compose down --remove-orphans
```

## Daily Commands

| Task | Command |
| --- | --- |
| Start app | `docker compose up -d --build db api frontend --remove-orphans` |
| Run migrations | `docker compose run --rm api alembic upgrade head` |
| Seed CSV data | `docker compose run --rm api python scripts/seed_local_db.py` |
| Migrate + seed shortcut | `docker compose run --rm seed` |
| Backend tests | `docker compose run --rm test` |
| Frontend smoke tests | `docker compose run --rm frontend-test` |
| Follow logs | `docker compose logs -f --tail=100 api frontend db` |
| Container status | `docker compose ps` |
| Restart app services | `docker compose restart api frontend` |
| Stop containers | `docker compose down --remove-orphans` |
| Stop and delete DB volume | `docker compose down --remove-orphans -v` |

Use `--build` in the start command. It keeps the API image fresh after changes to `Dockerfile`, `requirements.txt`, `scripts/`, `alembic/`, or other files copied into the image. The frontend is mounted from `frontend/src`, so most frontend edits only need a browser refresh.

## Database And Migrations

Local Docker uses:

```text
postgresql+psycopg://lms:lms@db:5432/lms
```

The database is exposed to your host as `localhost:5433` to avoid conflicts with any PostgreSQL already running on `5432`. Override it if needed:

```bash
POSTGRES_HOST_PORT=55432 docker compose up -d db
```

Run migrations:

```bash
docker compose run --rm api alembic upgrade head
```

Check current migration:

```bash
docker compose run --rm api alembic current
```

Create a future migration after model changes:

```bash
docker compose run --rm api alembic revision --autogenerate -m "describe schema change"
```

Why Alembic:

- It versions schema changes instead of relying on `create_all`.
- It makes local PostgreSQL closer to Supabase/PostgreSQL production.
- It lets you review DB changes before applying them.
- It prevents seed scripts from silently hiding missing migrations.

## Data Import

Seed from the clean CSV:

```bash
docker compose run --rm api python scripts/seed_local_db.py
```

Seed demo data:

```bash
docker compose run --rm api python scripts/seed_local_db.py --demo
```

Seed another CSV:

```bash
docker compose run --rm api python scripts/seed_local_db.py --csv data/library-cbg-clean.csv
```

The seed is destructive only for `APP_ENV=local` and `APP_ENV=test`. It refuses to run in other environments unless `--force` is passed.

The import summary is written to `data/local/last_seed_summary.json` and exposed through:

```bash
curl http://localhost:8000/import-summary | python3 -m json.tool
```

Each issue includes:

- `severity`: `warning` or `error`
- `code`: stable machine-readable issue code
- `row`, `field`, `value`
- `message`: human-readable explanation

Warnings are tolerable development data issues. Errors are intended for future blocking import cases.

## Tests

Backend unit and functional tests:

```bash
docker compose run --rm test
```

This resets `lms_test`, runs `alembic upgrade head`, and executes pytest with coverage.

Frontend smoke tests:

```bash
docker compose run --rm frontend-test
```

This starts dependencies, runs migrations/seed through the `seed` service, and executes Playwright in mobile and desktop viewports. The first run pulls a large official Playwright image; later runs are much faster.

The smoke suite checks:

- Mobile first screen exposes search, loan, return, and navigation without initial scroll
- Search for `gracia`
- Navigation through main workspace views
- Loan and return modals open and close
- ES/EN language switch persists after reload
- `favicon.svg` and `favicon.ico` return `200`
- No critical app console errors or app/API `404+` responses

Local helper:

```bash
./scripts/test.sh
```

## Logs And Debugging

Follow app logs:

```bash
docker compose logs -f --tail=100 api frontend
```

Follow DB logs:

```bash
docker compose logs -f --tail=100 db
```

Show recent logs once:

```bash
docker compose logs --tail=100 api frontend db
```

List containers:

```bash
docker compose ps
```

Open a shell in the API image:

```bash
docker compose run --rm api sh
```

Press `Ctrl+C` while following logs to exit the log viewer; it does not stop containers.

## API Checks

Health:

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

Search:

```bash
curl "http://localhost:8000/search?q=gracia&limit=5" | python3 -m json.tool
```

Paginated books:

```bash
curl "http://localhost:8000/books?limit=5&offset=0" | python3 -m json.tool
```

Open loans:

```bash
curl "http://localhost:8000/loans?status=open&limit=5" | python3 -m json.tool
```

Overdue loans:

```bash
curl "http://localhost:8000/loans?status=overdue&limit=5" | python3 -m json.tool
```

List endpoints return data plus `meta`:

```json
{
  "books": [],
  "meta": {
    "limit": 5,
    "offset": 0,
    "returned": 0,
    "total": 0,
    "has_more": false
  }
}
```

Errors use:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "field_errors": []
  }
}
```

## Environment Variables

`.env.example`:

```env
APP_ENV=local
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql+psycopg://lms:lms@db:5432/lms
AUTO_CREATE_DB=false
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://frontend:8080
```

Key behavior:

- `APP_ENV=local`: permits local destructive seed/reset commands
- `DATABASE_URL`: points Docker services to PostgreSQL
- `AUTO_CREATE_DB=false`: schema should come from Alembic migrations
- `CORS_ORIGINS`: allows browser and Docker-based frontend calls
- `POSTGRES_HOST_PORT`: optional host port override for the `db` service

## Local Without Docker

Use this only when debugging outside containers.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

SQLite fallback:

```bash
export APP_ENV=local
export DATABASE_URL=sqlite:///./data/local/library.db
export AUTO_CREATE_DB=true
export CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
python scripts/seed_local_db.py
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend in another terminal:

```bash
python3 -m http.server 8080 --directory frontend/src
```

Local JS smoke tests require Node dependencies:

```bash
npm ci
FRONTEND_BASE_URL=http://localhost:8080 LMS_API_BASE_URL=http://localhost:8000 npm run smoke:frontend
```

## Project Structure

```text
alembic/
  env.py
  versions/
data/
  library-cbg-clean.csv
  local/last_seed_summary.json
docker/
  postgres/init-test-db.sql
frontend/src/
  application/
  domain/
  infrastructure/
  ui/
scripts/
  reset_database.py
  seed_local_db.py
  test.sh
src/
  application/
  domain/
  infrastructure/
tests/
  functional/
  frontend/
  unit/
```

## Troubleshooting

Port `5432` already in use:

The compose file maps PostgreSQL to host `5433` by default. If `5433` is also busy, run:

```bash
POSTGRES_HOST_PORT=55432 docker compose up -d db
```

Seed fails with missing tables:

```bash
docker compose run --rm api alembic upgrade head
docker compose run --rm api python scripts/seed_local_db.py
```

Reset local PostgreSQL data completely:

```bash
docker compose down --remove-orphans -v
docker compose up -d --build db api frontend --remove-orphans
docker compose run --rm api alembic upgrade head
docker compose run --rm api python scripts/seed_local_db.py
```

Check API health from inside Docker:

```bash
docker compose run --rm api python -c "import urllib.request; print(urllib.request.urlopen('http://api:8000/health').read().decode())"
```

## Future Direction

- Move PostgreSQL hosting to Supabase with the same Alembic-managed schema discipline
- Add richer import validation for production CSVs
- Keep backend use cases as the source of business rules
- Consider React/Vite only after the current operational workflow is stable enough to justify a frontend framework migration
