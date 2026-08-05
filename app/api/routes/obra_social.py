from fastapi import APIRouter, status

from app.core.dependencies import DbSession
from app.schemas.obra_social import (
    ObraSocialCreate,
    ObraSocialResponse,
    ObraSocialUpdate,
)
from app.services.obra_social_service import ObraSocialService

router = APIRouter(prefix="/obra-social", tags=["obra-social"])


@router.post("/", response_model=ObraSocialResponse, status_code=status.HTTP_201_CREATED)
def create_obra_social(payload: ObraSocialCreate, db: DbSession) -> ObraSocialResponse:
    """Crea una nueva obra social."""
    return ObraSocialService(db).create(payload)


@router.get("/{obra_social_id}", response_model=ObraSocialResponse)
def get_obra_social(obra_social_id: int, db: DbSession) -> ObraSocialResponse:
    """Devuelve una obra social por id."""
    return ObraSocialService(db).get(obra_social_id)


@router.get("/", response_model=list[ObraSocialResponse])
def list_obra_sociales(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
) -> list[ObraSocialResponse]:
    """Lista obras sociales paginadas."""
    return ObraSocialService(db).list(skip=skip, limit=limit)


@router.put("/{obra_social_id}", response_model=ObraSocialResponse)
def update_obra_social(
    obra_social_id: int,
    payload: ObraSocialUpdate,
    db: DbSession,
) -> ObraSocialResponse:
    """Actualiza una obra social."""
    return ObraSocialService(db).update(obra_social_id, payload)


@router.delete("/{obra_social_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_obra_social(obra_social_id: int, db: DbSession) -> None:
    """Elimina una obra social."""
    ObraSocialService(db).delete(obra_social_id)
