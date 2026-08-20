from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema


class FacturaCreate(BaseSchema):
    paciente_nombre: str = Field(min_length=1, max_length=200)
    consultorio: str = Field(min_length=1, max_length=100)
    dni: str | None = None
    obra_social: str | None = None
    nro_afiliado: str | None = None
    periodo: str | None = None
    fecha_emision: str | None = None
    nro_factura: str | None = None
    sesiones: int = Field(ge=0, default=0)
    monto: float = Field(ge=0, default=0)
    porcentaje: float | None = None
    fecha_pago: str | None = None


class FacturaResponse(FacturaCreate):
    id: int
    created_at: datetime
