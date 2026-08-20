from sqlalchemy.orm import Session

from app.models.config_models import ConfigPorcentaje, ConfigPrecio
from app.repositories.config_repository import ConfigPorcentajeRepository, ConfigPrecioRepository


DEFAULT_PRECIOS = {
    "particular": 20000.0,
    "obra_social": 15000.0,
    "discapacidad": 12000.0,
}

DEFAULT_PORCENTAJES = {
    "particular": 15.0,
    "obra_social": 20.0,
}


class ConfigService:
    def __init__(self, db: Session) -> None:
        self.precios_repo = ConfigPrecioRepository(db)
        self.porcentajes_repo = ConfigPorcentajeRepository(db)

    def get_precios(self) -> dict[str, float]:
        result = {}
        for clave, default in DEFAULT_PRECIOS.items():
            instance = self.precios_repo.get_by_clave(clave)
            result[clave] = instance.valor if instance else default
        return result

    def set_precio(self, clave: str, valor: float) -> ConfigPrecio:
        return self.precios_repo.upsert(clave, valor)

    def get_porcentajes(self) -> dict[str, float]:
        result = {}
        for clave, default in DEFAULT_PORCENTAJES.items():
            instance = self.porcentajes_repo.get_by_clave(clave)
            result[clave] = instance.valor if instance else default
        return result

    def set_porcentaje(self, clave: str, valor: float) -> ConfigPorcentaje:
        return self.porcentajes_repo.upsert(clave, valor)
