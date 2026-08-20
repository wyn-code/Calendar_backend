from fastapi import APIRouter, status

from app.core.dependencies import DbSession
from app.schemas.factura import FacturaCreate, FacturaResponse
from app.services.factura_service import FacturaService

router = APIRouter(prefix="/facturas", tags=["facturas"])


@router.post("/", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
def create_factura(payload: FacturaCreate, db: DbSession) -> FacturaResponse:
    return FacturaService(db).create(payload)


@router.get("/", response_model=list[FacturaResponse])
def list_facturas(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
) -> list[FacturaResponse]:
    return FacturaService(db).list(skip=skip, limit=limit)


@router.get("/{factura_id}", response_model=FacturaResponse)
def get_factura(factura_id: int, db: DbSession) -> FacturaResponse:
    return FacturaService(db).get(factura_id)
