from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repositorio de pacientes."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Patient)

    def get_by_nombre_completo(self, nombre_completo: str) -> Patient | None:
        """Busca un paciente por nombre completo (insensible a mayúsculas)."""
        stmt = select(Patient).where(
            func.lower(Patient.nombre_completo) == nombre_completo.lower()
        )
        return self.db.scalars(stmt).first()

    def get_all(
        self, *, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> list[Patient]:
        """Devuelve una lista paginada de pacientes, ordenada por nombre."""
        stmt = select(Patient)
        if search:
            stmt = stmt.where(
                func.lower(Patient.nombre_completo).contains(search.lower())
            )
        stmt = stmt.order_by(Patient.nombre_completo).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))
