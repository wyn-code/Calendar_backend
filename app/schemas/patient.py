from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema


class PatientBase(BaseSchema):
    nombre_completo: str = Field(min_length=1, max_length=200)
    telefono: str | None = Field(default=None, max_length=50)
    obra_social_id: int | None = None
    observaciones: str | None = None


class PatientCreate(PatientBase):
    """Datos necesarios para crear un paciente."""


class PatientUpdate(BaseSchema):
    """Campos opcionales para actualizar un paciente."""

    nombre_completo: str | None = Field(default=None, min_length=1, max_length=200)
    telefono: str | None = Field(default=None, max_length=50)
    obra_social_id: int | None = None
    observaciones: str | None = None


class PatientResponse(PatientBase):
    id: int
    user_id: int | None
    created_at: datetime
    updated_at: datetime
