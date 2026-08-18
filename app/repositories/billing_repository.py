import calendar
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.obra_social import ObraSocial

CONSULTORIO_NEUROVITAL = "Neurovital"
TIPO_CONSULTA_OBRA_SOCIAL = "Obra Social"


def get_neurovital_session_counts(
    db: Session, year: int, month: int
) -> dict[str, int]:
    """Cuenta citas de Neurovital del mes, agrupadas por tipo de consulta.

    Retorna ``{"obra_social_count": N, "particular_count": M}``.
    """
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    stmt = (
        select(
            Appointment.tipo_consulta,
            func.count(Appointment.id),
        )
        .join(Patient, Appointment.patient_id == Patient.id)
        .where(
            Appointment.fecha >= first_day,
            Appointment.fecha <= last_day,
            Patient.consultorio == CONSULTORIO_NEUROVITAL,
        )
        .group_by(Appointment.tipo_consulta)
    )

    rows = dict(db.execute(stmt).all())

    obra_social_count = rows.get(TIPO_CONSULTA_OBRA_SOCIAL, 0)
    particular_count = sum(
        count for tipo, count in rows.items() if tipo != TIPO_CONSULTA_OBRA_SOCIAL
    )

    return {"obra_social_count": obra_social_count, "particular_count": particular_count}
