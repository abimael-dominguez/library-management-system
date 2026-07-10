"""FastAPI application factory and HTTP route definitions.

Route handlers are intentionally thin — they parse the incoming request,
delegate to a use case via the ``ServiceContainer``, and serialise the
domain entity into a response DTO.  No business logic lives here.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from ..persistence.database import get_db, init_db
from ..persistence.seed import read_seed_summary
from .serializers import serialize_book, serialize_employee, serialize_loan, serialize_member


def _error_payload(code: str, message: str, field_errors: list[dict] | None = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "field_errors": field_errors or [],
        }
    }


def _pagination_meta(*, limit: int, offset: int, returned: int, total: int) -> dict[str, int | bool]:
    return {
        "limit": limit,
        "offset": offset,
        "returned": returned,
        "total": total,
        "has_more": offset + returned < total,
    }


def _raise_bad_request(exc: DomainError) -> None:
    """Translate a domain-layer validation error into an HTTP 400 response."""
    raise HTTPException(
        status_code=400,
        detail={"code": "domain_error", "message": str(exc), "field_errors": []},
    ) from exc


def create_app(*, auto_seed: bool = False) -> FastAPI:
    """Build and return a fully-configured FastAPI application."""
    if auto_seed:
        raise RuntimeError("Auto-seeding is disabled. Use scripts/seed_local_db.py explicitly.")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.auto_create_db:
            init_db()
        yield

    app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail and "message" in detail:
            payload = _error_payload(
                code=str(detail["code"]),
                message=str(detail["message"]),
                field_errors=list(detail.get("field_errors") or []),
            )
        else:
            default_code = "not_found" if exc.status_code == 404 else "http_error"
            payload = _error_payload(code=default_code, message=str(detail))
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        field_errors = [
            {
                "field": ".".join(str(part) for part in error.get("loc", []) if part != "body"),
                "message": error.get("msg", "Invalid value."),
                "type": error.get("type", "validation_error"),
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                code="validation_error",
                message="Request validation failed.",
                field_errors=field_errors,
            ),
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
    def list_books(
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
    ):
        container = ServiceContainer(db)
        books = container.list_books.execute(limit=limit, offset=offset)
        total = container.list_books.count()
        return {
            "books": [serialize_book(book) for book in books],
            "meta": _pagination_meta(limit=limit, offset=offset, returned=len(books), total=total),
        }

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
            raise HTTPException(status_code=404, detail={"code": "book_not_found", "message": "Book not found."})
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
    def list_members(
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
    ):
        container = ServiceContainer(db)
        members = container.list_members.execute(limit=limit, offset=offset)
        total = container.list_members.count()
        return {
            "members": [serialize_member(member) for member in members],
            "meta": _pagination_meta(limit=limit, offset=offset, returned=len(members), total=total),
        }

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
    def list_employees(
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
    ):
        container = ServiceContainer(db)
        employees = container.list_employees.execute(limit=limit, offset=offset)
        total = container.list_employees.count()
        return {
            "employees": [serialize_employee(employee) for employee in employees],
            "meta": _pagination_meta(limit=limit, offset=offset, returned=len(employees), total=total),
        }

    @app.post("/employees", status_code=201)
    def create_employee(payload: EmployeeCreateRequest, db: Session = Depends(get_db)):
        try:
            employee = ServiceContainer(db).create_employee.execute(payload=payload)
        except DomainError as exc:
            _raise_bad_request(exc)
        return serialize_employee(employee)

    # ------------------------------------------------------------------
    # Loans
    # ------------------------------------------------------------------

    @app.get("/loans")
    def list_loans(
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        status: str = Query(default="all", pattern="^(all|open|overdue|returned)$"),
        db: Session = Depends(get_db),
    ):
        container = ServiceContainer(db)
        loans = container.list_loans.execute(limit=limit, offset=offset, status=status)
        total = container.list_loans.count(status=status)
        return {
            "loans": [serialize_loan(loan) for loan in loans],
            "meta": _pagination_meta(limit=limit, offset=offset, returned=len(loans), total=total),
        }

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
            raise HTTPException(status_code=404, detail={"code": "loan_not_found", "message": "Loan not found."})
        return serialize_loan(loan)

    @app.put("/loans/{loan_id}/return")
    def return_loan(loan_id: str, payload: LoanReturnRequest, db: Session = Depends(get_db)):
        try:
            loan = ServiceContainer(db).return_loan.execute(loan_id=loan_id, payload=payload)
        except DomainError as exc:
            _raise_bad_request(exc)
        return serialize_loan(loan)

    return app
