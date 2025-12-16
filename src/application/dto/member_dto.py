from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date


class CreateMemberRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    address: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class MemberResponse(BaseModel):
    member_id: str
    first_name: str
    last_name: str
    email: str
    address: Optional[str]
    phone: Optional[str]
    registration_date: Optional[date]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]