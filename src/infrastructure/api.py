from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ..application.dto import (
    BookCreateRequest,
    BookResponse,
    EmployeeCreateRequest,
    EmployeeResponse,
    LoanCreateRequest,
    LoanResponse,
    LoanReturnRequest,
    MemberCreateRequest,
    MemberResponse,
)
from ..application.use_cases import BookService, EmployeeService, LoanService, MemberService
from ..domain.entities.book import Book
from ..domain.entities.employee import Employee
from ..domain.entities.loan import Loan
from ..domain.entities.member import Member
from ..domain.exceptions import DomainError
from .database import SessionLocal, get_db, init_db
from .repositories import (
    SqlAlchemyBookCopyRepository,
    SqlAlchemyBookRepository,
    SqlAlchemyEmployeeRepository,
    SqlAlchemyLoanRepository,
    SqlAlchemyMemberRepository,
)
from .seed import read_seed_summary, seed_demo_data
from .settings import settings


def serialize_book(book: Book) -> BookResponse:
    return BookResponse(
        book_id=book.book_id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        publisher=book.publisher,
        publication_year=book.publication_year,
        genre=book.genre,
        pages=book.pages,
        max_loan_weeks=book.max_loan_weeks,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        first_available_copy_id=book.first_available_copy_id,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


def serialize_member(member: Member) -> MemberResponse:
    return MemberResponse(
        member_id=member.member_id,
        first_name=member.first_name,
        last_name=member.last_name,
        email=member.email,
        address=member.address,
        phone=member.phone,
        registration_date=member.registration_date,
        status=member.status.value,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )


def serialize_employee(employee: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        employee_id=employee.employee_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        position=employee.position,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
    )


def serialize_loan(loan: Loan) -> LoanResponse:
    return LoanResponse(
        loan_id=loan.loan_id,
        book_copy_id=loan.book_copy_id,
        member_id=loan.member_id,
        employee_id=loan.employee_id,
        loan_date=loan.loan_date,
        due_date=loan.due_date,
        actual_return_date=loan.actual_return_date,
        status=loan.status.value,
        book_title=loan.book_title,
        book_author=loan.book_author,
        member_name=loan.member_name,
        employee_name=loan.employee_name,
        created_at=loan.created_at,
        updated_at=loan.updated_at,
    )


def build_services(db: Session):
    book_repo = SqlAlchemyBookRepository(db)
    book_copy_repo = SqlAlchemyBookCopyRepository(db)
    member_repo = SqlAlchemyMemberRepository(db)
    employee_repo = SqlAlchemyEmployeeRepository(db)
    loan_repo = SqlAlchemyLoanRepository(db)
    return {
        "book_service": BookService(book_repo, book_copy_repo, db.commit, db.rollback),
        "member_service": MemberService(member_repo, db.commit, db.rollback),
        "employee_service": EmployeeService(employee_repo, db.commit, db.rollback),
        "loan_service": LoanService(
            loan_repo,
            book_copy_repo,
            member_repo,
            employee_repo,
            db.commit,
            db.rollback,
        ),
    }


def raise_bad_request(exc: DomainError) -> None:
    raise HTTPException(status_code=400, detail=str(exc)) from exc


def create_app(*, auto_seed: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.auto_create_db:
            init_db()
            if auto_seed:
                with SessionLocal() as db:
                    seed_demo_data(db)
        yield

    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    @app.get("/import-summary")
    def import_summary():
        return read_seed_summary()

    @app.get("/books")
    def list_books(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        services = build_services(db)
        books = services["book_service"].list_books(limit)
        return {"books": [serialize_book(book) for book in books]}

    @app.post("/books", status_code=201)
    def create_book(payload: BookCreateRequest, db: Session = Depends(get_db)):
        try:
            book = build_services(db)["book_service"].create_book(payload)
        except DomainError as exc:
            raise_bad_request(exc)
        return serialize_book(book)

    @app.get("/books/{book_id}")
    def get_book(book_id: str, db: Session = Depends(get_db)):
        book = build_services(db)["book_service"].get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found.")
        return serialize_book(book)

    @app.get("/search")
    def search_books(
        q: str = Query(..., min_length=1),
        limit: int = Query(default=10, ge=1, le=50),
        db: Session = Depends(get_db),
    ):
        books = build_services(db)["book_service"].search_books(q, limit)
        return {"books": [serialize_book(book) for book in books]}

    @app.get("/autocomplete")
    def autocomplete(
        q: str = Query(..., min_length=1),
        type: str = Query(..., pattern="^(book|member)$"),
        limit: int = Query(default=5, ge=1, le=20),
        db: Session = Depends(get_db),
    ):
        services = build_services(db)
        if type == "member":
            results = services["member_service"].autocomplete_members(q, limit)
            return {"results": [result.model_dump() for result in results]}
        books = services["book_service"].search_books(q, limit)
        return {
            "results": [
                {"id": book.book_id, "title": book.title, "author": book.author}
                for book in books
            ]
        }

    @app.get("/members")
    def list_members(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        members = build_services(db)["member_service"].list_members(limit)
        return {"members": [serialize_member(member) for member in members]}

    @app.post("/members", status_code=201)
    def create_member(payload: MemberCreateRequest, db: Session = Depends(get_db)):
        try:
            member = build_services(db)["member_service"].create_member(payload)
        except DomainError as exc:
            raise_bad_request(exc)
        return serialize_member(member)

    @app.get("/employees")
    def list_employees(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        employees = build_services(db)["employee_service"].list_employees(limit)
        return {"employees": [serialize_employee(employee) for employee in employees]}

    @app.post("/employees", status_code=201)
    def create_employee(payload: EmployeeCreateRequest, db: Session = Depends(get_db)):
        employee = build_services(db)["employee_service"].create_employee(payload)
        return serialize_employee(employee)

    @app.get("/loans")
    def list_loans(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
        loans = build_services(db)["loan_service"].list_loans(limit)
        return {"loans": [serialize_loan(loan) for loan in loans]}

    @app.post("/loans", status_code=201)
    def create_loan(payload: LoanCreateRequest, db: Session = Depends(get_db)):
        try:
            loan = build_services(db)["loan_service"].create_loan(payload)
        except DomainError as exc:
            raise_bad_request(exc)
        return serialize_loan(loan)

    @app.get("/loans/{loan_id}")
    def get_loan(loan_id: str, db: Session = Depends(get_db)):
        loan = build_services(db)["loan_service"].get_loan(loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")
        return serialize_loan(loan)

    @app.put("/loans/{loan_id}/return")
    def return_loan(loan_id: str, payload: LoanReturnRequest, db: Session = Depends(get_db)):
        try:
            loan = build_services(db)["loan_service"].return_loan(loan_id, payload)
        except DomainError as exc:
            raise_bad_request(exc)
        return serialize_loan(loan)

    return app
