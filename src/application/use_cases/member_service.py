from typing import List, Optional
import uuid
from datetime import datetime, date

from ...domain.entities.member import Member, MemberStatus
from ...domain.repositories.member_repository import MemberRepository
from ..dto.member_dto import CreateMemberRequest, MemberResponse


class MemberService:
    def __init__(self, member_repo: MemberRepository):
        self.member_repo = member_repo

    async def create_member(self, request: CreateMemberRequest) -> MemberResponse:
        member_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        member = Member(
            member_id=member_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            address=request.address,
            phone=request.phone,
            registration_date=date.today(),
            status=MemberStatus.ACTIVE,
            created_at=now,
            updated_at=now
        )
        
        created_member = await self.member_repo.create_member(member)
        return MemberResponse(**created_member.__dict__)

    async def get_member(self, member_id: str) -> Optional[MemberResponse]:
        member = await self.member_repo.get_member_by_id(member_id)
        if not member:
            return None
        return MemberResponse(**member.__dict__)

    async def search_members(self, query: str, limit: int = 10) -> List[MemberResponse]:
        members = await self.member_repo.search_members(query, limit)
        return [MemberResponse(**member.__dict__) for member in members]

    async def autocomplete_members(self, query: str, limit: int = 5) -> List[dict]:
        return await self.member_repo.autocomplete_members(query, limit)

    async def list_members(self, limit: int = 50, last_key: Optional[str] = None) -> tuple[List[MemberResponse], Optional[str]]:
        members, next_key = await self.member_repo.list_members(limit, last_key)
        return [MemberResponse(**member.__dict__) for member in members], next_key