from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from enum import Enum


class MemberStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class Member:
    member_id: str
    first_name: str
    last_name: str
    email: str
    address: Optional[str] = None
    phone: Optional[str] = None
    registration_date: Optional[date] = None
    status: MemberStatus = MemberStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"