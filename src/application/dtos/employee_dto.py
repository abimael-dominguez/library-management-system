from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EmployeeCreateRequest(BaseModel):
    """Input DTO for registering a new library employee."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)


class EmployeeResponse(BaseModel):
    """Output DTO returned when querying employee data."""

    employee_id: str
    first_name: str
    last_name: str
    position: str
    created_at: datetime | None
    updated_at: datetime | None
