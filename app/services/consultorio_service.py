from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.consultorio import Consultorio
from app.repositories.consultorio_repository import ConsultorioRepository
from app.schemas.consultorio import ConsultorioCreate, ConsultorioUpdate


class ConsultorioService:
    def __init__(self, db: Session) -> None:
        self.repository = ConsultorioRepository(db)

    def create(self, data: ConsultorioCreate) -> Consultorio:
        return self.repository.create(data)

    def update(self, obj_id: int, data: ConsultorioUpdate) -> Consultorio:
        instance = self.get(obj_id)
        return self.repository.update(instance, data)

    def delete(self, obj_id: int) -> None:
        instance = self.get(obj_id)
        self.repository.delete(instance)

    def get(self, obj_id: int) -> Consultorio:
        instance = self.repository.get_by_id(obj_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Consultorio no encontrado"
            )
        return instance

    def list(self, *, skip: int = 0, limit: int = 100) -> list[Consultorio]:
        return self.repository.get_all(skip=skip, limit=limit)
