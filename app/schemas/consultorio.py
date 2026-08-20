from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema


class ConsultorioBase(BaseSchema):
    nombre: str = Field(min_length=1, max_length=100)


class ConsultorioCreate(ConsultorioBase):
    pass


class ConsultorioUpdate(BaseSchema):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)


class ConsultorioResponse(ConsultorioBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime
