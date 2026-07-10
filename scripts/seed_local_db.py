#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.persistence.database import SessionLocal, init_db
from src.infrastructure.persistence.seed import seed_demo_data, seed_from_csv
from src.infrastructure.config.settings import settings


SAFE_SEED_ENVS = {"local", "test"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate the local library database from a CSV file.")
    parser.add_argument(
        "--csv",
        default="data/library-cbg-clean.csv",
        help="Path to the spreadsheet-export CSV file.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Load demo data instead of importing the CSV.",
    )
    parser.add_argument(
        "--rebuild-schema",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Drop and recreate the schema before seeding. Disabled by default; prefer Alembic migrations.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow seeding outside APP_ENV=local/test. Intended only for controlled maintenance.",
    )
    return parser.parse_args()


def ensure_safe_environment(*, force: bool) -> None:
    if settings.app_env in SAFE_SEED_ENVS or force:
        return
    raise SystemExit(
        "Refusing to run destructive seed outside APP_ENV=local/test. "
        "Set APP_ENV=local for development or pass --force for controlled maintenance."
    )


def main() -> None:
    args = parse_args()
    ensure_safe_environment(force=args.force)
    if settings.auto_create_db:
        init_db()
    with SessionLocal() as db:
        if args.demo:
            summary = seed_demo_data(db, rebuild_schema=args.rebuild_schema)
            print("Local database reset with demo data.")
        else:
            csv_path = PROJECT_ROOT / args.csv
            summary = seed_from_csv(db, csv_path, rebuild_schema=args.rebuild_schema)
            print(f"Local database synchronized from {csv_path}.")
    print(
        "Books: {books}, Copies: {copies}, Members: {members}, Employees: {employees}, "
        "Active loans: {active_loans}, Skipped active loans: {skipped_active_loans}, "
        "Skipped returned history: {skipped_loan_history}, Warnings: {warnings}, Errors: {errors}".format(
            books=summary.books,
            copies=summary.copies,
            members=summary.members,
            employees=summary.employees,
            active_loans=summary.active_loans,
            skipped_active_loans=summary.skipped_active_loans,
            skipped_loan_history=summary.skipped_loan_history,
            warnings=summary.warnings,
            errors=summary.errors,
        )
    )


if __name__ == "__main__":
    main()
