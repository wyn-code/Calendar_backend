import calendar
from datetime import date

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import DbSession
from app.core.config import settings
from app.models.appointment import Appointment
from app.models.config_models import ConfigPorcentaje
from app.models.patient import Patient

router = APIRouter(prefix="/billing", tags=["billing"])


class ConsultorioBilling(BaseModel):
    consultorio: str
    particular_sessions: int
    obra_social_sessions: int
    particular_amount: float
    obra_social_amount: float
    total: float
    total_bruto: float
    a_favor: float
    particular_pct: float
    obra_social_pct: float


class BillingPorConsultorioResponse(BaseModel):
    year: int
    month: int
    consultorios: list[ConsultorioBilling]
    total_a_pagar: float
    total_bruto: float
    a_favor: float


def _get_porcentaje(db: Session, clave: str, consultorio: str) -> float:
    """Lee el porcentaje de config_porcentajes para un consultorio, o devuelve el default."""
    defaults = {"particular": 15.0, "obra_social": 20.0}
    stmt = select(ConfigPorcentaje).where(
        ConfigPorcentaje.clave == clave,
        ConfigPorcentaje.consultorio == consultorio,
    )
    instance = db.scalars(stmt).first()
    return instance.valor if instance else defaults.get(clave, 15.0)


@router.get("/por-consultorio", response_model=BillingPorConsultorioResponse)
def get_billing_por_consultorio(
    db: DbSession,
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    consultorio: str | None = Query(None),
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
    for cons, tipo_consulta, count in rows:
        if cons not in consultorio_data:
            consultorio_data[cons] = {
                "particular_sessions": 0,
                "obra_social_sessions": 0,
            }
        if tipo_consulta == "Obra Social":
            consultorio_data[cons]["obra_social_sessions"] += count
        else:
            consultorio_data[cons]["particular_sessions"] += count

    consultorios_billing = []
    total_a_pagar = 0.0
    total_bruto = 0.0
    total_sessions = 0

    for cons, data in consultorio_data.items():
        pct_particular = _get_porcentaje(db, "particular", cons)
        pct_os = _get_porcentaje(db, "obra_social", cons)

        particular_amount = data["particular_sessions"] * (
            settings.BASE_SESSION_AMOUNT * pct_particular / 100
        )
        obra_social_amount = data["obra_social_sessions"] * (
            settings.BASE_SESSION_AMOUNT * pct_os / 100
        )
        consultorio_total = particular_amount + obra_social_amount
        sessions = data["particular_sessions"] + data["obra_social_sessions"]
        bruto = sessions * settings.BASE_SESSION_AMOUNT

        total_a_pagar += consultorio_total
        total_bruto += bruto
        total_sessions += sessions

        consultorios_billing.append(
            ConsultorioBilling(
                consultorio=cons,
                particular_sessions=data["particular_sessions"],
                obra_social_sessions=data["obra_social_sessions"],
                particular_amount=particular_amount,
                obra_social_amount=obra_social_amount,
                total=consultorio_total,
                total_bruto=bruto,
                a_favor=bruto - consultorio_total,
                particular_pct=pct_particular,
                obra_social_pct=pct_os,
            )
        )

    consultorios_billing.sort(key=lambda c: c.consultorio)

    if consultorio:
        consultorios_billing = [c for c in consultorios_billing if c.consultorio == consultorio]

    return BillingPorConsultorioResponse(
        year=year,
        month=month,
        consultorios=consultorios_billing,
        total_a_pagar=total_a_pagar,
        total_bruto=total_bruto,
        a_favor=total_bruto - total_a_pagar,
    )
