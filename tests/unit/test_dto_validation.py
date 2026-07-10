from datetime import date

import pytest
from pydantic import ValidationError

from src.application.dtos.book_dto import BookCreateRequest
from src.application.dtos.loan_dto import LoanCreateRequest, LoanReturnRequest
from src.application.dtos.member_dto import MemberCreateRequest


def test_book_create_defaults():
    payload = BookCreateRequest(title="Minimal", author="Author")
    assert payload.max_loan_weeks == 3
    assert payload.total_copies == 1


def test_book_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        BookCreateRequest(title="", author="Author")


def test_member_create_validates_email():
    with pytest.raises(ValidationError):
        MemberCreateRequest(first_name="Ana", last_name="Lopez", email="not-an-email")


def test_member_create_email_is_optional():
    payload = MemberCreateRequest(first_name="Ana", last_name="Lopez")
    assert payload.email is None


def test_loan_create_requires_ids():
    with pytest.raises(ValidationError):
        LoanCreateRequest(book_copy_id="", member_id="member-1", loan_date=date.today(), due_date=date.today())


def test_return_loan_payload_is_optional():
    payload = LoanReturnRequest()
    assert payload.actual_return_date is None
