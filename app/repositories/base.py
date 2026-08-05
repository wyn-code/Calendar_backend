from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """CRUD genérico reutilizable por todos los repositorios del dominio."""

    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    def create(self, obj_in: Any) -> ModelType:
        """Persiste una nueva entidad a partir de un schema."""
        instance = self.model(**obj_in.model_dump())
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, obj_id: int) -> ModelType | None:
        """Devuelve una entidad por su id, o `None` si no existe."""
        return self.db.get(self.model, obj_id)

    def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Devuelve una lista paginada de entidades."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def update(self, instance: ModelType, obj_in: Any) -> ModelType:
        """Aplica los campos presentes en `obj_in` sobre la entidad dada."""
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        """Elimina la entidad de la base de datos."""
        self.db.delete(instance)
        self.db.commit()
