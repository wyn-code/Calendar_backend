from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.config_models import Factura
from app.repositories.factura_repository import FacturaRepository
from app.schemas.factura import FacturaCreate


class FacturaService:
    def __init__(self, db: Session) -> None:
        self.repository = FacturaRepository(db)

    def create(self, data: FacturaCreate) -> Factura:
        return self.repository.create(data)

    def list(self, *, skip: int = 0, limit: int = 100) -> list[Factura]:
        return self.repository.get_all(skip=skip, limit=limit)

    def get(self, obj_id: int) -> Factura:
        instance = self.repository.get_by_id(obj_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada"
            )
        return instance
