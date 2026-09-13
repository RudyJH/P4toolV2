""" Pydantic models for user-related data structures. 
    Includes models for user creation, update, response, and 
    listing, with validation rules for fields like email, 
    username, and password strength."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Literal
import uuid
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    role: Literal["admin", "user", "viewer"] = "user"


class UserCreate(UserBase):
    """POST /users — password required."""
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    """PUT /users/{id} — all fields optional."""
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    first_name: str | None = None
    last_name: str | None = None
    role: Literal["admin", "user", "viewer"] | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    data: list[UserResponse]
    total: int
    page: int
    limit: int
