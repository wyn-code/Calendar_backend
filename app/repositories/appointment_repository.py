import calendar
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment
from app.models.patient import Patient
from app.repositories.base import BaseRepository

CONSULTORIO_EXPORTACION = "Neurovital"


class AppointmentRepository(BaseRepository[Appointment]):
    """Repositorio de turnos."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Appointment)

    def get_by_month(self, year: int, month: int) -> list[Appointment]:
        """Devuelve los turnos de un mes, con paciente y obra social cargados.

        Solo incluye turnos de pacientes del consultorio de exportación
        (`CONSULTORIO_EXPORTACION`). Usa `joinedload` para evitar N+1 al
        acceder a `patient.nombre_completo` y `obra_social.nombre` durante
        la exportación a Excel/PDF.
        """
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        stmt = (
            select(Appointment)
            .join(Appointment.patient)
            .options(joinedload(Appointment.patient), joinedload(Appointment.obra_social))
            .where(
                Appointment.fecha >= first_day,
                Appointment.fecha <= last_day,
                Patient.consultorio == CONSULTORIO_EXPORTACION,
            )
            .order_by(Appointment.fecha, Appointment.hora_inicio)
        )
        return list(self.db.scalars(stmt))
