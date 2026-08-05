from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nombre: str = Field(min_length=1, max_length=100)


class UserUpdate(BaseSchema):
    email: EmailStr | None = None
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    activo: bool | None = None


class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    nombre: str
    activo: bool
    created_at: datetime
