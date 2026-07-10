from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


BOOK_COPY_STATUSES = ("available", "damaged", "lost")
MEMBER_STATUSES = ("active", "inactive", "suspended")
LOAN_STATUSES = ("in_progress", "returned")


class TimestampMixin:
    """Adds ``created_at`` / ``updated_at`` columns to every ORM model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class BookModel(TimestampMixin, Base):
    __tablename__ = "book"

    book_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    isbn: Mapped[str | None] = mapped_column(String(17), unique=True)
    publisher: Mapped[str | None] = mapped_column(String(255))
    publication_year: Mapped[int | None] = mapped_column(Integer)
    genre: Mapped[str | None] = mapped_column(String(100))
    pages: Mapped[int | None] = mapped_column(Integer)
    max_loan_weeks: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    copies: Mapped[list["BookCopyModel"]] = relationship(
        back_populates="book",
    )


class BookCopyModel(TimestampMixin, Base):
    __tablename__ = "book_copy"
    __table_args__ = (
        CheckConstraint(f"status IN {BOOK_COPY_STATUSES}", name="ck_book_copy_status"),
    )

    book_copy_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("book.book_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False)

    book: Mapped["BookModel"] = relationship(back_populates="copies")
    loans: Mapped[list["LoanModel"]] = relationship(back_populates="book_copy")


class MemberModel(TimestampMixin, Base):
    __tablename__ = "member"
    __table_args__ = (
        CheckConstraint(f"status IN {MEMBER_STATUSES}", name="ck_member_status"),
    )

    member_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(254), unique=True)
    registration_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    loans: Mapped[list["LoanModel"]] = relationship(back_populates="member")


class EmployeeModel(TimestampMixin, Base):
    __tablename__ = "employee"

    employee_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)

    loans: Mapped[list["LoanModel"]] = relationship(back_populates="employee")


class LoanModel(TimestampMixin, Base):
    __tablename__ = "loan"
    __table_args__ = (
        CheckConstraint(f"status IN {LOAN_STATUSES}", name="ck_loan_status"),
        CheckConstraint("due_date >= loan_date", name="ck_due_date_after_loan_date"),
        CheckConstraint(
            "actual_return_date IS NULL OR actual_return_date >= loan_date",
            name="ck_actual_return_after_loan_date",
        ),
        CheckConstraint(
            "(status = 'returned' AND actual_return_date IS NOT NULL) "
            "OR (status = 'in_progress' AND actual_return_date IS NULL)",
            name="ck_loan_status_return_date_consistency",
        ),
    )

    loan_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    book_copy_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("book_copy.book_copy_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("member.member_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("employee.employee_id", ondelete="SET NULL"),
    )
    loan_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_return_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)

    book_copy: Mapped["BookCopyModel"] = relationship(back_populates="loans")
    member: Mapped["MemberModel"] = relationship(back_populates="loans")
    employee: Mapped["EmployeeModel"] = relationship(back_populates="loans")


Index(
    "ix_loan_one_active_copy",
    LoanModel.book_copy_id,
    unique=True,
    sqlite_where=(LoanModel.status == "in_progress"),
    postgresql_where=(LoanModel.status == "in_progress"),
)
