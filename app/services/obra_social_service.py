from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.obra_social import ObraSocial
from app.repositories.obra_social_repository import ObraSocialRepository
from app.schemas.obra_social import ObraSocialCreate, ObraSocialUpdate


class ObraSocialService:
    """Lógica de negocio de obras sociales."""

    def __init__(self, db: Session) -> None:
        self.repository = ObraSocialRepository(db)

    def create(self, data: ObraSocialCreate) -> ObraSocial:
        """Crea una nueva obra social."""
        return self.repository.create(data)

    def update(self, obj_id: int, data: ObraSocialUpdate) -> ObraSocial:
        """Actualiza una obra social existente."""
        instance = self.get(obj_id)
        return self.repository.update(instance, data)

    def delete(self, obj_id: int) -> None:
        """Elimina una obra social."""
        instance = self.get(obj_id)
        self.repository.delete(instance)

    def get(self, obj_id: int) -> ObraSocial:
        """Devuelve una obra social por id."""
        instance = self.repository.get_by_id(obj_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Obra social no encontrada"
            )
        return instance

    def list(self, *, skip: int = 0, limit: int = 100) -> list[ObraSocial]:
        """Devuelve una lista paginada de obras sociales."""
        return self.repository.get_all(skip=skip, limit=limit)
