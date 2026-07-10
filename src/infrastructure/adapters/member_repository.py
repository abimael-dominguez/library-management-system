from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ...domain.entities.member import Member, MemberStatus
from ...domain.interfaces.member_repository import MemberRepository
from ..persistence.models import MemberModel


def _to_domain_member(model: MemberModel) -> Member:
    """Map a MemberModel ORM instance to the domain Member entity."""
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
    """SQLAlchemy-backed implementation of the MemberRepository interface."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_member(self, member: Member) -> Member:
        self._db.add(
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
        model = self._db.get(MemberModel, member_id)
        return _to_domain_member(model) if model else None

    def search_members(self, query: str, limit: int = 10) -> list[Member]:
        term = f"%{query.lower()}%"
        stmt = (
            select(MemberModel)
            .where(
                or_(
                    func.lower(MemberModel.first_name).like(term),
                    func.lower(MemberModel.last_name).like(term),
                )
            )
            .order_by(MemberModel.first_name, MemberModel.last_name)
            .limit(limit)
        )
        return [_to_domain_member(model) for model in self._db.scalars(stmt).all()]

    def list_members(self, limit: int = 50, offset: int = 0) -> list[Member]:
        stmt = (
            select(MemberModel)
            .order_by(MemberModel.first_name, MemberModel.last_name)
            .offset(offset)
            .limit(limit)
        )
        return [_to_domain_member(model) for model in self._db.scalars(stmt).all()]

    def count_members(self) -> int:
        return int(self._db.scalar(select(func.count(MemberModel.member_id))) or 0)
