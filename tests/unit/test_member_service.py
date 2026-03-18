from src.application.dto.member_dto import MemberCreateRequest
from src.application.use_cases.member_service import MemberService
from src.infrastructure.repositories.member_repository import SqlAlchemyMemberRepository


def test_create_member_sets_defaults(db_session):
    service = MemberService(SqlAlchemyMemberRepository(db_session), db_session.commit, db_session.rollback)

    member = service.create_member(
        MemberCreateRequest(
            first_name="Ana",
            last_name="Lopez",
            email="ana.lopez@example.com",
        )
    )

    assert member.status == "active"
    assert member.registration_date is not None


def test_member_autocomplete_uses_full_name(db_session):
    service = MemberService(SqlAlchemyMemberRepository(db_session), db_session.commit, db_session.rollback)
    service.create_member(
        MemberCreateRequest(
            first_name="Carlos",
            last_name="Ramirez",
            email="carlos.ramirez@example.com",
        )
    )

    results = service.autocomplete_members("carlos")
    assert len(results) == 1
    assert results[0].name == "Carlos Ramirez"
