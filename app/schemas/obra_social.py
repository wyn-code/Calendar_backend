from pydantic import Field

from app.schemas.base import BaseSchema


class ObraSocialBase(BaseSchema):
    nombre: str = Field(min_length=1, max_length=100)


class ObraSocialCreate(ObraSocialBase):
    """Datos necesarios para crear una obra social."""


class ObraSocialUpdate(BaseSchema):
    """Campos opcionales para actualizar una obra social."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)


class ObraSocialResponse(ObraSocialBase):
    id: int
