from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.schemas.billing import MonthlyBillingResponse
from app.services.billing_service import calculate_monthly_total

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/total", response_model=MonthlyBillingResponse)
def get_monthly_billing(
    db: DbSession,
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
) -> MonthlyBillingResponse:
    """Devuelve el TOTAL A PAGAR de Neurovital para un mes/año dado."""
    return calculate_monthly_total(db, year, month)
