from src.application.dtos.member_dto import MemberCreateRequest
from src.application.use_cases.autocomplete_members import AutocompleteMembersUseCase
from src.application.use_cases.create_member import CreateMemberUseCase
from src.infrastructure.adapters.member_repository import SqlAlchemyMemberRepository
from src.infrastructure.adapters.unit_of_work import SqlAlchemyUnitOfWork


def test_create_member_sets_defaults(db_session):
    uow = SqlAlchemyUnitOfWork(db_session)
    member_repo = SqlAlchemyMemberRepository(db_session)
    create_member = CreateMemberUseCase(
        member_repo=member_repo,
        unit_of_work=uow,
    )

    member = create_member.execute(
        payload=MemberCreateRequest(
            first_name="Ana",
            last_name="Lopez",
            email="ana.lopez@example.com",
        )
    )

    assert member.status == "active"
    assert member.registration_date is not None


def test_member_autocomplete_uses_full_name(db_session):
    uow = SqlAlchemyUnitOfWork(db_session)
    member_repo = SqlAlchemyMemberRepository(db_session)
    create_member = CreateMemberUseCase(
        member_repo=member_repo,
        unit_of_work=uow,
    )
    autocomplete = AutocompleteMembersUseCase(member_repo=member_repo)

    create_member.execute(
        payload=MemberCreateRequest(
            first_name="Carlos",
            last_name="Ramirez",
            email="carlos.ramirez@example.com",
        )
    )

    results = autocomplete.execute(query="carlos")
    assert len(results) == 1
    assert results[0].name == "Carlos Ramirez"
