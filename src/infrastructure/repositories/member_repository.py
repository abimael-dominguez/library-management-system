from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ...domain.entities.member import Member, MemberStatus
from ...domain.repositories.member_repository import MemberRepository
from ..models import MemberModel


def to_domain_member(model: MemberModel) -> Member:
    return Member(
        member_id=model.member_id,
        first_name=model.first_name,
        last_name=model.last_name,
        email=model.email,
        address=model.address,
        phone=model.phone,
        registration_date=model.registration_date,
        status=MemberStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyMemberRepository(MemberRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_member(self, member: Member) -> Member:
        self.db.add(
            MemberModel(
                member_id=member.member_id,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
                address=member.address,
                phone=member.phone,
                registration_date=member.registration_date,
                status=member.status.value,
            )
        )
        return member

    def get_member_by_id(self, member_id: str) -> Member | None:
        model = self.db.get(MemberModel, member_id)
        return to_domain_member(model) if model else None

    def search_members(self, query: str, limit: int = 10) -> list[Member]:
        term = f"%{query.lower()}%"
        stmt = (
            select(MemberModel)
            .where(
                or_(
                    func.lower(MemberModel.first_name).like(term),
                    func.lower(MemberModel.last_name).like(term),
                    func.lower(MemberModel.email).like(term),
                )
            )
            .order_by(MemberModel.first_name, MemberModel.last_name)
            .limit(limit)
        )
        return [to_domain_member(model) for model in self.db.scalars(stmt).all()]

    def list_members(self, limit: int = 50) -> list[Member]:
        stmt = select(MemberModel).order_by(MemberModel.first_name, MemberModel.last_name).limit(limit)
        return [to_domain_member(model) for model in self.db.scalars(stmt).all()]
