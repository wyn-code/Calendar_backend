from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.billing_repository import get_neurovital_session_counts
from app.schemas.billing import MonthlyBillingResponse


def calculate_monthly_total(
    db: Session, year: int, month: int
) -> MonthlyBillingResponse:
    """Calcula el TOTAL A PAGAR de Neurovital para un mes dado.

    Aplica el porcentaje correspondiente según tipo de consulta:
    - Obra Social  → 20 % del valor base de la sesión
    - Particular   → 15 % del valor base de la sesión
    """
    counts = get_neurovital_session_counts(db, year, month)
    total_sessions = counts["obra_social_count"] + counts["particular_count"]

    os_commission = counts["obra_social_count"] * (
        settings.BASE_SESSION_AMOUNT * settings.NEUROVITAL_OBRA_SOCIAL_PERCENT / 100
    )
    particular_commission = counts["particular_count"] * (
        settings.BASE_SESSION_AMOUNT * settings.NEUROVITAL_PARTICULAR_PERCENT / 100
    )
    total_commission = os_commission + particular_commission

    return MonthlyBillingResponse(
        year=year,
        month=month,
        obra_social_sessions=counts["obra_social_count"],
        particular_sessions=counts["particular_count"],
        total_a_pagar=total_commission,
        a_favor=(total_sessions * settings.BASE_SESSION_AMOUNT) - total_commission,
    )
