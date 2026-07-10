from __future__ import annotations

from datetime import date
from uuid import uuid4

from ...domain.entities.member import Member, MemberStatus
from ...domain.exceptions import DomainError
from ...domain.interfaces.member_repository import MemberRepository
from ..dtos.member_dto import MemberCreateRequest
from ..interfaces.unit_of_work import UnitOfWork


class CreateMemberUseCase:
    """Registers a new library member inside a single transaction."""

    def __init__(self, member_repo: MemberRepository, unit_of_work: UnitOfWork) -> None:
        self._member_repo = member_repo
        self._unit_of_work = unit_of_work

    def execute(self, *, payload: MemberCreateRequest) -> Member:
        member = Member(
            member_id=str(uuid4()),
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email) if payload.email else None,
            address=payload.address,
            phone=payload.phone,
            registration_date=date.today(),
            status=MemberStatus.ACTIVE,
        )
        try:
            self._member_repo.create_member(member)
            self._unit_of_work.commit()
        except Exception as exc:
            self._unit_of_work.rollback()
            raise DomainError("Member could not be saved. Email may already exist.") from exc

        created = self._member_repo.get_member_by_id(member.member_id)
        if not created:
            raise DomainError("Member was created but could not be reloaded.")
        return created
