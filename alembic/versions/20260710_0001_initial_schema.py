"""Create initial library schema.

Revision ID: 20260710_0001
Revises:
Create Date: 2026-07-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260710_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "book",
        sa.Column("book_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("isbn", sa.String(length=17), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("genre", sa.String(length=100), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("max_loan_weeks", sa.Integer(), server_default="3", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("book_id"),
        sa.UniqueConstraint("isbn"),
    )
    op.create_index("ix_book_author", "book", ["author"])
    op.create_index("ix_book_title", "book", ["title"])

    op.create_table(
        "employee",
        sa.Column("employee_id", sa.String(length=36), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("position", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("employee_id"),
    )

    op.create_table(
        "member",
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("registration_date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('active', 'inactive', 'suspended')", name="ck_member_status"),
        sa.PrimaryKeyConstraint("member_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_member_first_name", "member", ["first_name"])
    op.create_index("ix_member_last_name", "member", ["last_name"])

    op.create_table(
        "book_copy",
        sa.Column("book_copy_id", sa.String(length=64), nullable=False),
        sa.Column("book_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="available", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('available', 'damaged', 'lost')", name="ck_book_copy_status"),
        sa.ForeignKeyConstraint(["book_id"], ["book.book_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("book_copy_id"),
    )
    op.create_index("ix_book_copy_book_id", "book_copy", ["book_id"])

    op.create_table(
        "loan",
        sa.Column("loan_id", sa.String(length=36), nullable=False),
        sa.Column("book_copy_id", sa.String(length=64), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("employee_id", sa.String(length=36), nullable=True),
        sa.Column("loan_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("actual_return_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="in_progress", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('in_progress', 'returned')", name="ck_loan_status"),
        sa.CheckConstraint("due_date >= loan_date", name="ck_due_date_after_loan_date"),
        sa.CheckConstraint(
            "actual_return_date IS NULL OR actual_return_date >= loan_date",
            name="ck_actual_return_after_loan_date",
        ),
        sa.CheckConstraint(
            "(status = 'returned' AND actual_return_date IS NOT NULL) "
            "OR (status = 'in_progress' AND actual_return_date IS NULL)",
            name="ck_loan_status_return_date_consistency",
        ),
        sa.ForeignKeyConstraint(["book_copy_id"], ["book_copy.book_copy_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employee.employee_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["member_id"], ["member.member_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("loan_id"),
    )
    op.create_index("ix_loan_book_copy_id", "loan", ["book_copy_id"])
    op.create_index("ix_loan_member_id", "loan", ["member_id"])
    op.create_index(
        "ix_loan_one_active_copy",
        "loan",
        ["book_copy_id"],
        unique=True,
        postgresql_where=sa.text("status = 'in_progress'"),
        sqlite_where=sa.text("status = 'in_progress'"),
    )


def downgrade() -> None:
    op.drop_index("ix_loan_one_active_copy", table_name="loan")
    op.drop_index("ix_loan_member_id", table_name="loan")
    op.drop_index("ix_loan_book_copy_id", table_name="loan")
    op.drop_table("loan")
    op.drop_index("ix_book_copy_book_id", table_name="book_copy")
    op.drop_table("book_copy")
    op.drop_index("ix_member_last_name", table_name="member")
    op.drop_index("ix_member_first_name", table_name="member")
    op.drop_table("member")
    op.drop_table("employee")
    op.drop_index("ix_book_title", table_name="book")
    op.drop_index("ix_book_author", table_name="book")
    op.drop_table("book")
