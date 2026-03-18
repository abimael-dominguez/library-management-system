from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EmployeeCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)


class EmployeeResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    position: str
    created_at: datetime | None
    updated_at: datetime | None
