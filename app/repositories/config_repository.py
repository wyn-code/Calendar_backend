from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.config_models import ConfigPrecio, ConfigPorcentaje
from app.repositories.base import BaseRepository


class ConfigPrecioRepository(BaseRepository[ConfigPrecio]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, ConfigPrecio)

    def get_by_clave(self, clave: str) -> ConfigPrecio | None:
        stmt = select(ConfigPrecio).where(ConfigPrecio.clave == clave)
        return self.db.scalars(stmt).first()

    def upsert(self, clave: str, valor: float) -> ConfigPrecio:
        instance = self.get_by_clave(clave)
        if instance:
            instance.valor = valor
            self.db.commit()
            self.db.refresh(instance)
            return instance
        instance = ConfigPrecio(clave=clave, valor=valor)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance


class ConfigPorcentajeRepository(BaseRepository[ConfigPorcentaje]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, ConfigPorcentaje)

    def get_by_clave(self, clave: str) -> ConfigPorcentaje | None:
        stmt = select(ConfigPorcentaje).where(ConfigPorcentaje.clave == clave)
        return self.db.scalars(stmt).first()

    def upsert(self, clave: str, valor: float) -> ConfigPorcentaje:
        instance = self.get_by_clave(clave)
        if instance:
            instance.valor = valor
            self.db.commit()
            self.db.refresh(instance)
            return instance
        instance = ConfigPorcentaje(clave=clave, valor=valor)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
