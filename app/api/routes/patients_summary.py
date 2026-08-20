import calendar
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import DbSession
from app.models.appointment import Appointment
from app.models.patient import Patient

router = APIRouter(prefix="/patients", tags=["patients"])


class PatientSummary(BaseModel):
    patient_id: int
    sesiones_mes: int
    ultima_factura: str | None


@router.get("/summary", response_model=list[PatientSummary])
def get_patients_summary(
    db: DbSession,
    year: int | None = None,
    month: int | None = None,
) -> list[PatientSummary]:
    """Devuelve sesiones del mes y última factura para cada paciente."""
    from datetime import datetime

    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    stmt = (
        select(
            Appointment.patient_id,
            func.count(Appointment.id).label("sesiones_mes"),
        )
        .where(
            Appointment.fecha >= first_day,
            Appointment.fecha <= last_day,
        )
        .group_by(Appointment.patient_id)
    )
    session_counts = {row[0]: row[1] for row in db.execute(stmt).all()}

    last_invoice_stmt = (
        select(
            Appointment.patient_id,
            func.max(Appointment.fecha).label("ultima_fecha"),
        )
        .group_by(Appointment.patient_id)
    )
    last_invoices = {row[0]: row[1] for row in db.execute(last_invoice_stmt).all()}

    all_patients = db.execute(select(Patient.id)).scalars().all()

    return [
        PatientSummary(
            patient_id=pid,
            sesiones_mes=session_counts.get(pid, 0),
            ultima_factura=str(last_invoices[pid]) if pid in last_invoices else None,
        )
        for pid in all_patients
    ]
