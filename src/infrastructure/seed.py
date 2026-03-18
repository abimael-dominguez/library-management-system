from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import BookCopyModel, BookModel, EmployeeModel, LoanModel, MemberModel


@dataclass
class SeedSummary:
    books: int = 0
    copies: int = 0
    members: int = 0
    employees: int = 0
    active_loans: int = 0
    warnings: int = 0


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def stable_id(kind: str, raw_value: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{kind}:{normalize_key(raw_value)}"))


def split_name(full_name: str) -> tuple[str, str]:
    parts = [part for part in full_name.split(" ") if part]
    if not parts:
        return "Unknown", "User"
    if len(parts) == 1:
        return parts[0], "Library"
    return parts[0], " ".join(parts[1:])


def parse_int(value: str | None, default: int | None = None) -> int | None:
    cleaned = normalize_text(value)
    if not cleaned:
        return default
    try:
        return int(cleaned)
    except ValueError:
        return default


def parse_date(value: str | None) -> date | None:
    cleaned = normalize_text(value)
    if not cleaned:
        return None
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        return None


def is_active_loan_status(status: str) -> bool:
    return normalize_key(status) in {"prestado", "prestamo"}


def reset_library_data(db: Session) -> None:
    db.execute(delete(LoanModel))
    db.execute(delete(BookCopyModel))
    db.execute(delete(BookModel))
    db.execute(delete(MemberModel))
    db.execute(delete(EmployeeModel))
    db.commit()


def ensure_member(db: Session, cache: dict[str, MemberModel], raw_name: str, summary: SeedSummary) -> MemberModel:
    name = normalize_text(raw_name)
    key = normalize_key(name)
    if key in cache:
        return cache[key]

    first_name, last_name = split_name(name)
    member = MemberModel(
        member_id=stable_id("member", name),
        first_name=first_name,
        last_name=last_name,
        email=f"{stable_id('member-email', name)}@local.library",
        status="active",
    )
    db.add(member)
    cache[key] = member
    summary.members += 1
    return member


def ensure_employee(db: Session, cache: dict[str, EmployeeModel], raw_name: str, summary: SeedSummary) -> EmployeeModel | None:
    name = normalize_text(raw_name)
    if not name or name == "-":
        return None

    key = normalize_key(name)
    if key in cache:
        return cache[key]

    first_name, last_name = split_name(name)
    employee = EmployeeModel(
        employee_id=stable_id("employee", name),
        first_name=first_name,
        last_name=last_name,
        position="Library Staff",
    )
    db.add(employee)
    cache[key] = employee
    summary.employees += 1
    return employee


def create_book_with_copies(db: Session, row: dict[str, str], summary: SeedSummary) -> tuple[BookModel, list[BookCopyModel]]:
    title = normalize_text(row.get("title"))
    author = normalize_text(row.get("author"))
    total_copies = max(parse_int(row.get("total_copies"), 1) or 1, 1)
    pages = parse_int(row.get("pages"))
    max_loan_weeks = max(parse_int(row.get("max_loan_weeks"), 3) or 3, 1)

    book_id = stable_id("book", f"{title}|{author}")
    book = BookModel(
        book_id=book_id,
        title=title,
        author=author,
        pages=pages,
        max_loan_weeks=max_loan_weeks,
        total_copies=total_copies,
    )
    db.add(book)
    copies: list[BookCopyModel] = []
    for number in range(1, total_copies + 1):
        copy = BookCopyModel(
            book_copy_id=f"{book_id}-{number:03d}",
            book_id=book_id,
            status="available",
        )
        db.add(copy)
        copies.append(copy)

    summary.books += 1
    summary.copies += total_copies
    return book, copies


def choose_available_copy(copies: list[BookCopyModel]) -> BookCopyModel | None:
    for copy in copies:
        if copy.status == "available":
            return copy
    return None


def seed_from_csv(db: Session, csv_path: Path, reset: bool = True) -> SeedSummary:
    if reset:
        reset_library_data(db)

    summary = SeedSummary()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    book_cache: dict[str, tuple[BookModel, list[BookCopyModel]]] = {}
    member_cache: dict[str, MemberModel] = {}
    employee_cache: dict[str, EmployeeModel] = {}

    for index, row in enumerate(rows, start=1):
        title = normalize_text(row.get("title"))
        author = normalize_text(row.get("author"))
        if not title or not author:
            summary.warnings += 1
            continue

        book_key = normalize_key(f"{title}|{author}")
        if book_key not in book_cache:
            book_cache[book_key] = create_book_with_copies(db, row, summary)
        book, copies = book_cache[book_key]

        member_name = normalize_text(row.get("member"))
        employee_name = normalize_text(row.get("employee"))
        if member_name:
            ensure_member(db, member_cache, member_name, summary)
        if employee_name:
            ensure_employee(db, employee_cache, employee_name, summary)

        if not is_active_loan_status(row.get("status", "")):
            continue

        copy = choose_available_copy(copies)
        if not copy:
            summary.warnings += 1
            continue

        if not member_name:
            member_name = f"Pending Borrower {index}"
            summary.warnings += 1

        member = ensure_member(db, member_cache, member_name, summary)
        employee = ensure_employee(db, employee_cache, employee_name, summary)

        loan_date = parse_date(row.get("loan_date")) or date.today()
        due_date = parse_date(row.get("due_date")) or (loan_date + timedelta(weeks=book.max_loan_weeks))
        if due_date < loan_date:
            due_date = loan_date + timedelta(weeks=book.max_loan_weeks)
            summary.warnings += 1

        copy.status = "loaned"
        db.add(
            LoanModel(
                loan_id=stable_id("loan", f"{copy.book_copy_id}|{member.member_id}|{loan_date.isoformat()}"),
                book_copy_id=copy.book_copy_id,
                member_id=member.member_id,
                employee_id=employee.employee_id if employee else None,
                loan_date=loan_date,
                due_date=due_date,
                actual_return_date=None,
                status="in_progress",
            )
        )
        summary.active_loans += 1

    db.commit()
    return summary


def seed_demo_data(db: Session) -> SeedSummary:
    reset_library_data(db)
    summary = SeedSummary()
    member = ensure_member(db, {}, "Ana Gomez", summary)
    employee = ensure_employee(db, {}, "Luis Herrera", summary)
    book = BookModel(
        book_id="book-demo-001",
        title="Clean Architecture",
        author="Robert C. Martin",
        isbn="9780134494166",
        publisher="Pearson",
        publication_year=2017,
        genre="Software",
        pages=432,
        max_loan_weeks=3,
        total_copies=2,
    )
    db.add(book)
    copy_one = BookCopyModel(book_copy_id="book-demo-001-001", book_id=book.book_id, status="available")
    copy_two = BookCopyModel(book_copy_id="book-demo-001-002", book_id=book.book_id, status="loaned")
    db.add_all([copy_one, copy_two])
    db.add(
        LoanModel(
            loan_id="loan-demo-001",
            book_copy_id=copy_two.book_copy_id,
            member_id=member.member_id,
            employee_id=employee.employee_id if employee else None,
            loan_date=date.today() - timedelta(days=3),
            due_date=date.today() + timedelta(days=18),
            status="in_progress",
        )
    )
    summary.books = 1
    summary.copies = 2
    summary.active_loans = 1
    db.commit()
    return summary
