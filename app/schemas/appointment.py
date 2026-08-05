from datetime import date, datetime, time
from typing import Self

from pydantic import Field, model_validator

from app.schemas.base import BaseSchema


class AppointmentBase(BaseSchema):
    patient_id: int
    obra_social_id: int | None = None
    fecha: date
    hora_inicio: time
    tipo_consulta: str = Field(min_length=1, max_length=50)
    observaciones: str | None = None


class AppointmentCreate(AppointmentBase):
    """Datos necesarios para crear un turno."""

    @model_validator(mode="after")
    def validar_obra_social(self) -> Self:
        if self.tipo_consulta == "Obra Social" and self.obra_social_id is None:
            raise ValueError(
                "El tipo de consulta 'Obra Social' requiere especificar obra_social_id."
            )
        return self


class AppointmentUpdate(BaseSchema):
    """Campos opcionales para actualizar un turno."""

    patient_id: int | None = None
    obra_social_id: int | None = None
    fecha: date | None = None
    hora_inicio: time | None = None
    tipo_consulta: str | None = Field(default=None, min_length=1, max_length=50)
    observaciones: str | None = None


class AppointmentResponse(AppointmentBase):
    id: int
    user_id: int | None
    created_at: datetime
    updated_at: datetime
