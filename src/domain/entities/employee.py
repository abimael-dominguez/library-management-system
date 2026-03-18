from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Employee:
    employee_id: str
    first_name: str
    last_name: str
    position: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
