from app.schemas.base import BaseSchema


class MonthlyBillingResponse(BaseSchema):
    """Resumen de facturación mensual de Neurovital."""

    year: int
    month: int
    obra_social_sessions: int
    particular_sessions: int
    total_a_pagar: float
    a_favor: float
