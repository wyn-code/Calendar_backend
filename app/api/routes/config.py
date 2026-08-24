from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.schemas.config_schema import (
    ConfigPorcentajeUpdate,
    ConfigPorcentajeResponse,
    ConfigPrecioUpdate,
    ConfigPrecioResponse,
    PreciosResponse,
    PorcentajesResponse,
)
from app.services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/precios", response_model=PreciosResponse)
def get_precios(db: DbSession) -> PreciosResponse:
    data = ConfigService(db).get_precios()
    return PreciosResponse(**data)


@router.put("/precios/{clave}", response_model=ConfigPrecioResponse)
def set_precio(
    clave: str,
    payload: ConfigPrecioUpdate,
    db: DbSession,
) -> ConfigPrecioResponse:
    instance = ConfigService(db).set_precio(clave, payload.valor)
    return ConfigPrecioResponse(id=instance.id, clave=instance.clave, valor=instance.valor)


@router.get("/porcentajes", response_model=PorcentajesResponse)
def get_porcentajes(
    db: DbSession,
    consultorio: str | None = None,
) -> PorcentajesResponse:
    data = ConfigService(db).get_porcentajes(consultorio=consultorio)
    return PorcentajesResponse(**data)


@router.put("/porcentajes/{clave}", response_model=ConfigPorcentajeResponse)
def set_porcentaje(
    clave: str,
    payload: ConfigPorcentajeUpdate,
    db: DbSession,
    consultorio: str | None = None,
) -> ConfigPorcentajeResponse:
    instance = ConfigService(db).set_porcentaje(clave, payload.valor, consultorio=consultorio)
    return ConfigPorcentajeResponse(
        id=instance.id, clave=instance.clave, valor=instance.valor
    )
