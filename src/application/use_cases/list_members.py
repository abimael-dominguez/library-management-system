from __future__ import annotations

from ...domain.entities.member import Member
from ...domain.interfaces.member_repository import MemberRepository


class ListMembersUseCase:
    """Retrieves a paginated list of library members."""

    def __init__(self, member_repo: MemberRepository) -> None:
        self._member_repo = member_repo

    def execute(self, *, limit: int = 50) -> list[Member]:
        return self._member_repo.list_members(limit)
