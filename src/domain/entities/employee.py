from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Employee:
    employee_id: str
    first_name: str
    last_name: str
    position: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"