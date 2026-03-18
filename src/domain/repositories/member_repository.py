from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.member import Member


class MemberRepository(ABC):
    @abstractmethod
    def create_member(self, member: Member) -> Member:
        raise NotImplementedError

    @abstractmethod
    def get_member_by_id(self, member_id: str) -> Member | None:
        raise NotImplementedError

    @abstractmethod
    def search_members(self, query: str, limit: int = 10) -> list[Member]:
        raise NotImplementedError

    @abstractmethod
    def list_members(self, limit: int = 50) -> list[Member]:
        raise NotImplementedError
