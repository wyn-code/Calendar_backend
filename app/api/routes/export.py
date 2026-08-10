from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.core.dependencies import DbSession
from app.services.calendario_service import MESES, CalendarioExcelService
from app.services.planilla_service import PlanillaPdfService

router = APIRouter(prefix="/export", tags=["export"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PDF_MEDIA_TYPE = "application/pdf"


@router.get("/calendario")
def export_calendario(
    db: DbSession,
    year: int = Query(ge=2000, le=2100, description="Año a exportar"),
    month: int = Query(ge=1, le=12, description="Mes a exportar (1-12)"),
) -> StreamingResponse:
    """Genera el calendario mensual en Excel (.xlsx) con el diseño de la web."""
    buffer = CalendarioExcelService(db).build(year, month)
    filename = f"calendario-turnos-{MESES[month - 1].lower()}-{year}.xlsx"
    return StreamingResponse(
        buffer,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/planilla-sesiones")
def export_planilla_sesiones(
    db: DbSession,
    year: int = Query(ge=2000, le=2100, description="Año a exportar"),
    month: int = Query(ge=1, le=12, description="Mes a exportar (1-12)"),
) -> StreamingResponse:
    """Genera la planilla mensual de sesiones por paciente en PDF."""
    buffer = PlanillaPdfService(db).build(year, month)
    filename = f"planilla-sesiones-{MESES[month - 1].lower()}-{year}.pdf"
    return StreamingResponse(
        buffer,
        media_type=PDF_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )