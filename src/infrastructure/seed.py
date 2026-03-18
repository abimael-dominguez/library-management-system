from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import BookCopyModel, BookModel, EmployeeModel, LoanModel, MemberModel


def seed_demo_data(db: Session) -> None:
    existing = db.scalar(select(MemberModel.member_id).limit(1))
    if existing:
        return

    member = MemberModel(
        member_id="member-demo-001",
        first_name="Ana",
        last_name="Gomez",
        email="ana.gomez@example.com",
        address="Calle Biblioteca 123",
        phone="555-0101",
        status="active",
    )
    employee = EmployeeModel(
        employee_id="employee-demo-001",
        first_name="Luis",
        last_name="Herrera",
        position="Librarian",
    )
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
    copy_one = BookCopyModel(
        book_copy_id="book-demo-001-001",
        book_id=book.book_id,
        status="available",
    )
    copy_two = BookCopyModel(
        book_copy_id="book-demo-001-002",
        book_id=book.book_id,
        status="loaned",
    )
    loan = LoanModel(
        loan_id="loan-demo-001",
        book_copy_id=copy_two.book_copy_id,
        member_id=member.member_id,
        employee_id=employee.employee_id,
        loan_date=date.today() - timedelta(days=3),
        due_date=date.today() + timedelta(days=18),
        status="in_progress",
    )
    db.add_all([member, employee, book, copy_one, copy_two, loan])
    db.commit()
