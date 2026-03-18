from src.application.dto.book_dto import BookCreateRequest
from src.application.use_cases.book_service import BookService
from src.infrastructure.repositories.book_repository import SqlAlchemyBookCopyRepository, SqlAlchemyBookRepository


def test_create_book_creates_copies(db_session):
    service = BookService(
        SqlAlchemyBookRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )

    result = service.create_book(
        BookCreateRequest(
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
    service = BookService(
        SqlAlchemyBookRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    service.create_book(BookCreateRequest(title="Python Programming", author="John Doe"))
    service.create_book(BookCreateRequest(title="Distributed Systems", author="Jane Smith"))

    results = service.search_books("python")
    assert len(results) == 1
    assert results[0].title == "Python Programming"

    author_results = service.search_books("jane")
    assert len(author_results) == 1
    assert author_results[0].author == "Jane Smith"


def test_get_book_returns_none_when_missing(db_session):
    service = BookService(
        SqlAlchemyBookRepository(db_session),
        SqlAlchemyBookCopyRepository(db_session),
        db_session.commit,
        db_session.rollback,
    )
    assert service.get_book("missing-book") is None
