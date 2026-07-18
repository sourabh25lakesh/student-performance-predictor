"""
Pydantic schemas for the User resource (request & response bodies).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for POST /auth/register"""

    name: str = Field(..., min_length=2, max_length=100, examples=["Jane Doe"])
    email: EmailStr = Field(..., examples=["jane.doe@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["StrongPass123"])


class UserLogin(BaseModel):
    """Payload for POST /auth/login"""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Public-facing representation of a User (never includes the password)."""

    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
