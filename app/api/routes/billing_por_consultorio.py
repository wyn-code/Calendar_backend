import calendar
from datetime import date

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import DbSession
from app.core.config import settings
from app.models.appointment import Appointment
from app.models.patient import Patient

router = APIRouter(prefix="/billing", tags=["billing"])


class ConsultorioBilling(BaseModel):
    consultorio: str
    particular_sessions: int
    obra_social_sessions: int
    particular_amount: float
    obra_social_amount: float
    total: float


class BillingPorConsultorioResponse(BaseModel):
    year: int
    month: int
    consultorios: list[ConsultorioBilling]
    total_a_pagar: float
    a_favor: float


@router.get("/por-consultorio", response_model=BillingPorConsultorioResponse)
def get_billing_por_consultorio(
    db: DbSession,
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
) -> BillingPorConsultorioResponse:
    """Desglose de facturación por consultorio y tipo de consulta."""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    stmt = (
        select(
            Patient.consultorio,
            Appointment.tipo_consulta,
            func.count(Appointment.id),
        )
        .join(Patient, Appointment.patient_id == Patient.id)
        .where(
            Appointment.fecha >= first_day,
            Appointment.fecha <= last_day,
        )
        .group_by(Patient.consultorio, Appointment.tipo_consulta)
    )
    rows = db.execute(stmt).all()

    consultorio_data: dict[str, dict] = {}
    for consultorio, tipo_consulta, count in rows:
        if consultorio not in consultorio_data:
            consultorio_data[consultorio] = {
                "particular_sessions": 0,
                "obra_social_sessions": 0,
            }
        if tipo_consulta == "Obra Social":
            consultorio_data[consultorio]["obra_social_sessions"] += count
        else:
            consultorio_data[consultorio]["particular_sessions"] += count

    consultorios_billing = []
    total_a_pagar = 0.0
    total_sessions = 0

    for consultorio, data in consultorio_data.items():
        particular_amount = data["particular_sessions"] * (
            settings.BASE_SESSION_AMOUNT * settings.NEUROVITAL_PARTICULAR_PERCENT / 100
        )
        obra_social_amount = data["obra_social_sessions"] * (
            settings.BASE_SESSION_AMOUNT * settings.NEUROVITAL_OBRA_SOCIAL_PERCENT / 100
        )
        consultorio_total = particular_amount + obra_social_amount
        total_a_pagar += consultorio_total
        total_sessions += data["particular_sessions"] + data["obra_social_sessions"]

        consultorios_billing.append(
            ConsultorioBilling(
                consultorio=consultorio,
                particular_sessions=data["particular_sessions"],
                obra_social_sessions=data["obra_social_sessions"],
                particular_amount=particular_amount,
                obra_social_amount=obra_social_amount,
                total=consultorio_total,
            )
        )

    consultorios_billing.sort(key=lambda c: c.consultorio)

    return BillingPorConsultorioResponse(
        year=year,
        month=month,
        consultorios=consultorios_billing,
        total_a_pagar=total_a_pagar,
        a_favor=(total_sessions * settings.BASE_SESSION_AMOUNT) - total_a_pagar,
    )
