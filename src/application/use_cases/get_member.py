from __future__ import annotations

from ...domain.entities.member import Member
from ...domain.interfaces.member_repository import MemberRepository


class GetMemberUseCase:
    """Retrieves a single library member by ID."""

    def __init__(self, member_repo: MemberRepository) -> None:
        self._member_repo = member_repo

    def execute(self, *, member_id: str) -> Member | None:
        return self._member_repo.get_member_by_id(member_id)
