from src.application.dtos.book_dto import BookCreateRequest
from src.application.use_cases.create_book import CreateBookUseCase
from src.application.use_cases.get_book import GetBookUseCase
from src.application.use_cases.search_books import SearchBooksUseCase
from src.infrastructure.adapters.book_repository import SqlAlchemyBookCopyRepository, SqlAlchemyBookRepository
from src.infrastructure.adapters.unit_of_work import SqlAlchemyUnitOfWork


def test_create_book_creates_copies(db_session):
    uow = SqlAlchemyUnitOfWork(db_session)
    book_repo = SqlAlchemyBookRepository(db_session)
    book_copy_repo = SqlAlchemyBookCopyRepository(db_session)
    create_book = CreateBookUseCase(
        book_repo=book_repo,
        book_copy_repo=book_copy_repo,
        unit_of_work=uow,
    )

    result = create_book.execute(
        payload=BookCreateRequest(
            title="Test Book",
            author="Test Author",
            isbn="9780123456789",
            total_copies=2,
        )
    )

    assert result.title == "Test Book"
    assert result.available_copies == 2
    assert result.first_available_copy_id.endswith("-001")


def test_search_books_matches_title_and_author(db_session):
    uow = SqlAlchemyUnitOfWork(db_session)
    book_repo = SqlAlchemyBookRepository(db_session)
    book_copy_repo = SqlAlchemyBookCopyRepository(db_session)
    create_book = CreateBookUseCase(
        book_repo=book_repo,
        book_copy_repo=book_copy_repo,
        unit_of_work=uow,
    )
    search_books = SearchBooksUseCase(
        book_repo=book_repo,
        book_copy_repo=book_copy_repo,
    )
    create_book.execute(payload=BookCreateRequest(title="Python Programming", author="John Doe"))
    create_book.execute(payload=BookCreateRequest(title="Distributed Systems", author="Jane Smith"))

    results = search_books.execute(query="python")
    assert len(results) == 1
    assert results[0].title == "Python Programming"

    author_results = search_books.execute(query="jane")
    assert len(author_results) == 1
    assert author_results[0].author == "Jane Smith"


def test_get_book_returns_none_when_missing(db_session):
    book_repo = SqlAlchemyBookRepository(db_session)
    book_copy_repo = SqlAlchemyBookCopyRepository(db_session)
    get_book = GetBookUseCase(
        book_repo=book_repo,
        book_copy_repo=book_copy_repo,
    )
    assert get_book.execute(book_id="missing-book") is None
