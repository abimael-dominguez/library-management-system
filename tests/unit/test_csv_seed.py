from pathlib import Path

from sqlalchemy import select

from src.infrastructure.persistence.models import BookCopyModel, BookModel, EmployeeModel, LoanModel, MemberModel
from src.infrastructure.persistence.seed import seed_from_csv


def test_seed_from_csv_imports_books_and_active_loans(db_session, tmp_path):
    csv_path = tmp_path / "library.csv"
    csv_path.write_text(
        "\n".join(
            [
                "title,author,total_copies,pages,max_loan_weeks,status,employee,member,loan_date,due_date,actual_return_date",
                "Book One,Author One,2,100,3,Prestado,Ana Staff,Carlos Reader,2026-03-01,2026-03-22,",
                "Book Two,Author Two,1,200,4,Entregado,Ana Staff,Carlos Reader,2026-02-01,2026-02-22,",
                "Book Three,,1,150,2,Prestado,,, , ,",
            ]
        ),
        encoding="utf-8",
    )

    summary = seed_from_csv(db_session, csv_path, write_summary_file=False)

    assert summary.books == 3
    assert summary.copies == 4
    assert summary.active_loans == 1
    assert summary.skipped_active_loans == 1
    assert summary.skipped_loan_history == 1
    assert summary.warnings > 0
    assert summary.errors == 0
    issues = summary.to_dict()["issues"]
    assert all(issue["severity"] == "warning" for issue in issues)
    assert {issue["code"] for issue in issues} >= {
        "missing_author",
        "active_loan_missing_loan_date",
        "returned_history_missing_actual_return_date",
    }
    assert len(db_session.scalars(select(BookModel)).all()) == 3
    assert len(db_session.scalars(select(LoanModel)).all()) == 1
    assert len(db_session.scalars(select(MemberModel)).all()) == 1
    assert len(db_session.scalars(select(EmployeeModel)).all()) == 1

    loaned_copy = db_session.scalar(select(BookCopyModel).where(BookCopyModel.status == "loaned"))
    assert loaned_copy is None

    unknown_author = db_session.scalar(select(BookModel).where(BookModel.title == "Book Three"))
    assert unknown_author is not None
    assert unknown_author.author == "Unknown Author"
