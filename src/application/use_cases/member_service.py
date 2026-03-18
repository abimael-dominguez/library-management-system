from __future__ import annotations

from datetime import date
from uuid import uuid4

from ...domain.entities.member import Member, MemberStatus
from ...domain.exceptions import DomainError
from ...domain.repositories.member_repository import MemberRepository
from ..dto.member_dto import MemberAutocompleteResult, MemberCreateRequest


class MemberService:
    def __init__(self, member_repo: MemberRepository, commit, rollback):
        self.member_repo = member_repo
        self.commit = commit
        self.rollback = rollback

    def list_members(self, limit: int = 50) -> list[Member]:
        return self.member_repo.list_members(limit)

    def get_member(self, member_id: str) -> Member | None:
        return self.member_repo.get_member_by_id(member_id)

    def autocomplete_members(self, query: str, limit: int = 5) -> list[MemberAutocompleteResult]:
        members = self.member_repo.search_members(query, limit)
        return [MemberAutocompleteResult(id=member.member_id, name=member.full_name) for member in members]

    def create_member(self, payload: MemberCreateRequest) -> Member:
        member = Member(
            member_id=str(uuid4()),
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email),
            address=payload.address,
            phone=payload.phone,
            registration_date=date.today(),
            status=MemberStatus.ACTIVE,
        )
        try:
            self.member_repo.create_member(member)
            self.commit()
        except Exception as exc:
            self.rollback()
            raise DomainError("Member could not be saved. Email may already exist.") from exc

        created = self.member_repo.get_member_by_id(member.member_id)
        if not created:
            raise DomainError("Member was created but could not be reloaded.")
        return created
