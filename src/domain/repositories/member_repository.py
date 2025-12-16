from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.member import Member


class MemberRepository(ABC):
    @abstractmethod
    async def create_member(self, member: Member) -> Member:
        pass

    @abstractmethod
    async def get_member_by_id(self, member_id: str) -> Optional[Member]:
        pass

    @abstractmethod
    async def search_members(self, query: str, limit: int = 10) -> List[Member]:
        pass

    @abstractmethod
    async def autocomplete_members(self, query: str, limit: int = 5) -> List[dict]:
        pass

    @abstractmethod
    async def list_members(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[Member], Optional[str]]:
        pass

    @abstractmethod
    async def update_member(self, member: Member) -> Member:
        pass

    @abstractmethod
    async def delete_member(self, member_id: str) -> bool:
        pass