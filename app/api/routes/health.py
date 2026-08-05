from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Verifica que la API y la base de datos respondan correctamente."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        return {"status": "degraded", "database": "unavailable"}

    return {"status": "ok", "database": "ok"}
