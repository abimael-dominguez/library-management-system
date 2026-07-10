from __future__ import annotations

import csv
import json
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import delete
from sqlalchemy.orm import Session

from .database import Base
from .models import BookCopyModel, BookModel, EmployeeModel, LoanModel, MemberModel


SUMMARY_OUTPUT_PATH = Path("data/local/last_seed_summary.json")


@dataclass
class SeedSummary:
    books: int = 0
    copies: int = 0
    members: int = 0
    employees: int = 0
    active_loans: int = 0
    skipped_active_loans: int = 0
    skipped_loan_history: int = 0
    warnings: int = 0
    csv_path: str | None = None
    issues: list[dict[str, str | int | None]] | None = None

    def to_dict(self) -> dict[str, int | str | None | list[dict[str, str | int | None]]]:
        return {
            "books": self.books,
            "copies": self.copies,
            "members": self.members,
            "employees": self.employees,
            "active_loans": self.active_loans,
            "skipped_active_loans": self.skipped_active_loans,
            "skipped_loan_history": self.skipped_loan_history,
            "warnings": self.warnings,
            "csv_path": self.csv_path,
            "issues": self.issues or [],
        }

    def warn(
        self,
        message: str,
        *,
        row: int | None = None,
        field: str | None = None,
        value: str | None = None,
    ) -> None:
        self.warnings += 1
        if self.issues is None:
            self.issues = []
        self.issues.append({"row": row, "field": field, "value": value, "message": message})


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
        return parts[0], "Unknown"
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


def looks_like_date(value: str) -> bool:
    cleaned = normalize_text(value)
    if not cleaned:
        return False
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            datetime.strptime(cleaned, fmt)
            return True
        except ValueError:
            continue
    return False


def is_active_loan_status(status: str) -> bool:
    return normalize_key(status) in {"prestado", "prestamo"}


def is_returned_loan_status(status: str) -> bool:
    return normalize_key(status) == "entregado"


def has_loan_history(row: dict[str, str]) -> bool:
    return any(
        normalize_text(row.get(field)).strip("-")
        for field in ("employee", "member", "loan_date", "due_date", "actual_return_date")
    )


def parse_member_details(raw_name: str) -> tuple[str, str | None, str | None]:
    parts = [normalize_text(part) for part in raw_name.split(",") if normalize_text(part)]
    if not parts:
        return "", None, None

    name = parts[0]
    phone_parts = [part for part in parts[1:] if any(character.isdigit() for character in part)]
    address_parts = [part for part in parts[1:] if part not in phone_parts]
    phone = phone_parts[0] if phone_parts else None
    address = ", ".join(address_parts) or None
    return name, phone, address


def reset_library_data(db: Session, *, rebuild_schema: bool = False) -> None:
    if rebuild_schema:
        bind = db.get_bind()
        Base.metadata.drop_all(bind=bind)
        Base.metadata.create_all(bind=bind)
        db.commit()
        return

    db.execute(delete(LoanModel))
    db.execute(delete(BookCopyModel))
    db.execute(delete(BookModel))
    db.execute(delete(MemberModel))
    db.execute(delete(EmployeeModel))
    db.commit()


def ensure_member(
    db: Session,
    cache: dict[str, MemberModel],
    raw_name: str,
    summary: SeedSummary,
) -> MemberModel:
    name, phone, address = parse_member_details(raw_name)
    name = normalize_text(name)
    key = normalize_key(name)
    if key in cache:
        member = cache[key]
        if phone and not member.phone:
            member.phone = phone
        if address and not member.address:
            member.address = address
        return member

    first_name, last_name = split_name(name)
    member = MemberModel(
        member_id=stable_id("member", name),
        first_name=first_name,
        last_name=last_name,
        email=None,
        address=address,
        phone=phone,
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


def create_book_with_copies(
    db: Session,
    row: dict[str, str],
    summary: SeedSummary,
    row_number: int,
) -> tuple[BookModel, list[BookCopyModel]]:
    title = normalize_text(row.get("title"))
    author = normalize_text(row.get("author"))
    if not author:
        author = "Unknown Author"
        summary.warn("Missing author; imported with Unknown Author.", row=row_number, field="author")
    if not normalize_text(row.get("total_copies")):
        summary.warn("Missing total_copies; defaulted to 1.", row=row_number, field="total_copies")
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


def choose_available_copy(
    copies: list[BookCopyModel],
    active_copy_ids: set[str],
) -> BookCopyModel | None:
    for copy in copies:
        if copy.status == "available" and copy.book_copy_id not in active_copy_ids:
            return copy
    return None


def seed_from_csv(
    db: Session,
    csv_path: Path,
    reset: bool = True,
    rebuild_schema: bool = False,
    write_summary_file: bool = True,
) -> SeedSummary:
    if reset:
        reset_library_data(db, rebuild_schema=rebuild_schema)

    summary = SeedSummary()
    summary.csv_path = str(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    book_cache: dict[str, tuple[BookModel, list[BookCopyModel]]] = {}
    member_cache: dict[str, MemberModel] = {}
    employee_cache: dict[str, EmployeeModel] = {}
    active_copy_ids: set[str] = set()

    for index, row in enumerate(rows, start=1):
        row_number = index + 1
        title = normalize_text(row.get("title"))
        author = normalize_text(row.get("author"))
        if not title:
            summary.warn("Missing title; row skipped.", row=row_number, field="title")
            continue

        book_key = normalize_key(f"{title}|{author}")
        if book_key not in book_cache:
            book_cache[book_key] = create_book_with_copies(db, row, summary, row_number)
        book, copies = book_cache[book_key]

        member_name = normalize_text(row.get("member"))
        employee_name = normalize_text(row.get("employee"))
        if member_name and member_name != "-" and not looks_like_date(member_name):
            ensure_member(db, member_cache, member_name, summary)
        if employee_name:
            ensure_employee(db, employee_cache, employee_name, summary)

        if not is_active_loan_status(row.get("status", "")):
            if is_returned_loan_status(row.get("status", "")) and has_loan_history(row):
                summary.skipped_loan_history += 1
                summary.warn(
                    "Returned loan history has no actual return date; loan history was not imported.",
                    row=row_number,
                    field="actual_return_date",
                )
            continue

        copy = choose_available_copy(copies, active_copy_ids)
        if not copy:
            summary.warn("No available copy left for active loan; loan skipped.", row=row_number, field="total_copies")
            continue

        loan_date = parse_date(row.get("loan_date"))
        due_date = parse_date(row.get("due_date"))
        if not loan_date:
            summary.skipped_active_loans += 1
            summary.warn(
                "Active loan skipped because loan_date is missing or invalid.",
                row=row_number,
                field="loan_date",
                value=normalize_text(row.get("loan_date")) or None,
            )
            continue
        if not member_name or member_name == "-" or looks_like_date(member_name):
            summary.skipped_active_loans += 1
            summary.warn(
                "Active loan skipped because member is missing or invalid.",
                row=row_number,
                field="member",
                value=member_name or None,
            )
            continue
        if not due_date:
            due_date = loan_date + timedelta(weeks=book.max_loan_weeks)
            summary.warn(
                "Missing or invalid due date; derived from loan_date and max_loan_weeks.",
                row=row_number,
                field="due_date",
                value=normalize_text(row.get("due_date")) or None,
            )
        if loan_date and due_date and due_date < loan_date:
            summary.skipped_active_loans += 1
            summary.warn("Active loan skipped because due date is before loan date.", row=row_number, field="due_date")
            continue

        member = ensure_member(db, member_cache, member_name, summary)
        employee = ensure_employee(db, employee_cache, employee_name, summary)

        active_copy_ids.add(copy.book_copy_id)
        db.add(
            LoanModel(
                loan_id=stable_id(
                    "loan",
                    f"{copy.book_copy_id}|{member.member_id}|{loan_date.isoformat() if loan_date else 'unknown'}",
                ),
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
    if write_summary_file:
        write_seed_summary(summary)
    return summary


def seed_demo_data(
    db: Session,
    *,
    rebuild_schema: bool = False,
    write_summary_file: bool = True,
) -> SeedSummary:
    reset_library_data(db, rebuild_schema=rebuild_schema)
    summary = SeedSummary()
    summary.csv_path = "demo"
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
    )
    db.add(book)
    copy_one = BookCopyModel(book_copy_id="book-demo-001-001", book_id=book.book_id, status="available")
    copy_two = BookCopyModel(book_copy_id="book-demo-001-002", book_id=book.book_id, status="available")
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
    if write_summary_file:
        write_seed_summary(summary)
    return summary


def write_seed_summary(summary: SeedSummary) -> None:
    SUMMARY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUTPUT_PATH.write_text(
        json.dumps(summary.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def read_seed_summary() -> dict[str, int | str | None | list[dict[str, str | int | None]]]:
    if not SUMMARY_OUTPUT_PATH.exists():
        return {
            "books": 0,
            "copies": 0,
            "members": 0,
            "employees": 0,
            "active_loans": 0,
            "skipped_active_loans": 0,
            "skipped_loan_history": 0,
            "warnings": 0,
            "csv_path": None,
            "issues": [],
        }
    return json.loads(SUMMARY_OUTPUT_PATH.read_text(encoding="utf-8"))
