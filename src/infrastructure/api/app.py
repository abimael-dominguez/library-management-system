"""FastAPI application factory and HTTP route definitions.

Route handlers are intentionally thin — they parse the incoming request,
delegate to a use case via the ``ServiceContainer``, and serialise the
domain entity into a response DTO.  No business logic lives here.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ...application.dtos import (
    BookCreateRequest,
    EmployeeCreateRequest,
    LoanCreateRequest,
    LoanReturnRequest,
    MemberCreateRequest,
)
from ...domain.exceptions import DomainError
from ..config.container import ServiceContainer
from ..config.settings import settings
from ..persistence.database import SessionLocal, get_db, init_db
from ..persistence.seed import read_seed_summary, seed_demo_data
from .serializers import serialize_book, serialize_employee, serialize_loan, serialize_member


def _raise_bad_request(exc: DomainError) -> None:
    """Translate a domain-layer validation error into an HTTP 400 response."""
    raise HTTPException(status_code=400, detail=str(exc)) from exc


def create_app(*, auto_seed: bool = False) -> FastAPI:
    """Build and return a fully-configured FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.auto_create_db:
            init_db()
            if auto_seed:
                with SessionLocal() as db:
                    seed_demo_data(db)
        yield

    app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Health & diagnostics
    # ------------------------------------------------------------------

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    @app.get("/import-summary")
    def import_summary():
        return read_seed_summary()

    # ------------------------------------------------------------------
    # Books
    # ------------------------------------------------------------------

    @app.get("/books")
    def list_books(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        container = ServiceContainer(db)
        books = container.list_books.execute(limit=limit)
        return {"books": [serialize_book(book) for book in books]}

    @app.post("/books", status_code=201)
    def create_book(payload: BookCreateRequest, db: Session = Depends(get_db)):
        try:
            book = ServiceContainer(db).create_book.execute(payload=payload)
        except DomainError as exc:
            _raise_bad_request(exc)
        return serialize_book(book)

    @app.get("/books/{book_id}")
    def get_book(book_id: str, db: Session = Depends(get_db)):
        book = ServiceContainer(db).get_book.execute(book_id=book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found.")
        return serialize_book(book)

    @app.get("/search")
    def search_books(
        q: str = Query(..., min_length=1),
        limit: int = Query(default=10, ge=1, le=50),
        db: Session = Depends(get_db),
    ):
        books = ServiceContainer(db).search_books.execute(query=q, limit=limit)
        return {"books": [serialize_book(book) for book in books]}

    @app.get("/autocomplete")
    def autocomplete(
        q: str = Query(..., min_length=1),
        type: str = Query(..., pattern="^(book|member)$"),
        limit: int = Query(default=5, ge=1, le=20),
        db: Session = Depends(get_db),
    ):
        container = ServiceContainer(db)
        if type == "member":
            results = container.autocomplete_members.execute(query=q, limit=limit)
            return {"results": [result.model_dump() for result in results]}
        books = container.search_books.execute(query=q, limit=limit)
        return {
            "results": [
                {"id": book.book_id, "title": book.title, "author": book.author}
                for book in books
            ]
        }

    # ------------------------------------------------------------------
    # Members
    # ------------------------------------------------------------------

    @app.get("/members")
    def list_members(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        members = ServiceContainer(db).list_members.execute(limit=limit)
        return {"members": [serialize_member(member) for member in members]}

    @app.post("/members", status_code=201)
    def create_member(payload: MemberCreateRequest, db: Session = Depends(get_db)):
        try:
            member = ServiceContainer(db).create_member.execute(payload=payload)
        except DomainError as exc:
            _raise_bad_request(exc)
        return serialize_member(member)

    # ------------------------------------------------------------------
    # Employees
    # ------------------------------------------------------------------

    @app.get("/employees")
    def list_employees(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        employees = ServiceContainer(db).list_employees.execute(limit=limit)
        return {"employees": [serialize_employee(employee) for employee in employees]}

    @app.post("/employees", status_code=201)
    def create_employee(payload: EmployeeCreateRequest, db: Session = Depends(get_db)):
        employee = ServiceContainer(db).create_employee.execute(payload=payload)
        return serialize_employee(employee)

    # ------------------------------------------------------------------
    # Loans
    # ------------------------------------------------------------------

    @app.get("/loans")
    def list_loans(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        loans = ServiceContainer(db).list_loans.execute(limit=limit)
        return {"loans": [serialize_loan(loan) for loan in loans]}

    @app.post("/loans", status_code=201)
    def create_loan(payload: LoanCreateRequest, db: Session = Depends(get_db)):
        try:
            loan = ServiceContainer(db).create_loan.execute(payload=payload)
        except DomainError as exc:
            _raise_bad_request(exc)
        return serialize_loan(loan)

    @app.get("/loans/{loan_id}")
    def get_loan(loan_id: str, db: Session = Depends(get_db)):
        loan = ServiceContainer(db).get_loan.execute(loan_id=loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")
        return serialize_loan(loan)

    @app.put("/loans/{loan_id}/return")
    def return_loan(loan_id: str, payload: LoanReturnRequest, db: Session = Depends(get_db)):
        try:
            loan = ServiceContainer(db).return_loan.execute(loan_id=loan_id, payload=payload)
        except DomainError as exc:
            _raise_bad_request(exc)
        return serialize_loan(loan)

    return app
