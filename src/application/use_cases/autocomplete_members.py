from __future__ import annotations

from ..dtos.member_dto import MemberAutocompleteResult
from ...domain.interfaces.member_repository import MemberRepository


class AutocompleteMembersUseCase:
    """Returns lightweight autocomplete suggestions for member search."""

    def __init__(self, member_repo: MemberRepository) -> None:
        self._member_repo = member_repo

    def execute(self, *, query: str, limit: int = 5) -> list[MemberAutocompleteResult]:
        members = self._member_repo.search_members(query, limit)
        return [
            MemberAutocompleteResult(id=member.member_id, name=member.full_name)
            for member in members
        ]
