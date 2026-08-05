from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    """Lógica de negocio de turnos."""

    def __init__(self, db: Session) -> None:
        self.repository = AppointmentRepository(db)

    def create(self, data: AppointmentCreate) -> Appointment:
        """Crea un nuevo turno."""
        return self.repository.create(data)

    def update(self, obj_id: int, data: AppointmentUpdate) -> Appointment:
        """Actualiza un turno existente."""
        instance = self.get(obj_id)
        return self.repository.update(instance, data)

    def delete(self, obj_id: int) -> None:
        """Elimina un turno."""
        instance = self.get(obj_id)
        self.repository.delete(instance)

    def get(self, obj_id: int) -> Appointment:
        """Devuelve un turno por id."""
        instance = self.repository.get_by_id(obj_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado"
            )
        return instance

    def list(self, *, skip: int = 0, limit: int = 100) -> list[Appointment]:
        """Devuelve una lista paginada de turnos."""
        return self.repository.get_all(skip=skip, limit=limit)
