from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class MemberStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class Member:
    member_id: str
    first_name: str
    last_name: str
    email: str
    address: str | None = None
    phone: str | None = None
    registration_date: date | None = None
    status: MemberStatus = MemberStatus.ACTIVE
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
