from pydantic import Field

from app.schemas.base import BaseSchema


class ConfigPrecioBase(BaseSchema):
    clave: str = Field(min_length=1, max_length=50)
    valor: float = Field(ge=0)


class ConfigPrecioUpdate(BaseSchema):
    valor: float = Field(ge=0)


class ConfigPrecioResponse(ConfigPrecioBase):
    id: int


class ConfigPorcentajeBase(BaseSchema):
    clave: str = Field(min_length=1, max_length=50)
    valor: float = Field(ge=0, le=100)


class ConfigPorcentajeUpdate(BaseSchema):
    valor: float = Field(ge=0, le=100)


class ConfigPorcentajeResponse(ConfigPorcentajeBase):
    id: int


class PreciosResponse(BaseSchema):
    particular: float
    obra_social: float
    discapacidad: float


class PorcentajesResponse(BaseSchema):
    particular: float
    obra_social: float
