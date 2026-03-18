from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class MemberCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)


class MemberResponse(BaseModel):
    member_id: str
    first_name: str
    last_name: str
    email: str
    address: str | None
    phone: str | None
    registration_date: date | None
    status: str
    created_at: datetime | None
    updated_at: datetime | None


class MemberAutocompleteResult(BaseModel):
    id: str
    name: str
