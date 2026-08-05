from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    """Repositorio de turnos."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Appointment)
