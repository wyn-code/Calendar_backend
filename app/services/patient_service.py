from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:
    """Lógica de negocio de pacientes."""

    def __init__(self, db: Session) -> None:
        self.repository = PatientRepository(db)

    def create(self, data: PatientCreate) -> Patient:
        """Crea un nuevo paciente."""
        return self.repository.create(data)

    def update(self, obj_id: int, data: PatientUpdate) -> Patient:
        """Actualiza un paciente existente."""
        instance = self.get(obj_id)
        return self.repository.update(instance, data)

    def delete(self, obj_id: int) -> None:
        """Elimina un paciente."""
        instance = self.get(obj_id)
        self.repository.delete(instance)

    def get(self, obj_id: int) -> Patient:
        """Devuelve un paciente por id."""
        instance = self.repository.get_by_id(obj_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
            )
        return instance

    def list(self, *, skip: int = 0, limit: int = 100) -> list[Patient]:
        """Devuelve una lista paginada de pacientes."""
        return self.repository.get_all(skip=skip, limit=limit)
