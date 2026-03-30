#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.persistence.database import SessionLocal, init_db
from src.infrastructure.persistence.seed import seed_demo_data, seed_from_csv


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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db()
    with SessionLocal() as db:
        if args.demo:
            summary = seed_demo_data(db)
            print("Local database reset with demo data.")
        else:
            csv_path = PROJECT_ROOT / args.csv
            summary = seed_from_csv(db, csv_path)
            print(f"Local database synchronized from {csv_path}.")
    print(
        "Books: {books}, Copies: {copies}, Members: {members}, Employees: {employees}, "
        "Active loans: {active_loans}, Warnings: {warnings}".format(
            books=summary.books,
            copies=summary.copies,
            members=summary.members,
            employees=summary.employees,
            active_loans=summary.active_loans,
            warnings=summary.warnings,
        )
    )


if __name__ == "__main__":
    main()
