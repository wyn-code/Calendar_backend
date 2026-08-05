from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repositorio de pacientes."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Patient)
