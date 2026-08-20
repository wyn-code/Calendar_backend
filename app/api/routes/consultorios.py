from fastapi import APIRouter, status

from app.core.dependencies import DbSession
from app.schemas.consultorio import (
    ConsultorioCreate,
    ConsultorioResponse,
    ConsultorioUpdate,
)
from app.services.consultorio_service import ConsultorioService

router = APIRouter(prefix="/consultorios", tags=["consultorios"])


@router.post("/", response_model=ConsultorioResponse, status_code=status.HTTP_201_CREATED)
def create_consultorio(payload: ConsultorioCreate, db: DbSession) -> ConsultorioResponse:
    return ConsultorioService(db).create(payload)


@router.get("/", response_model=list[ConsultorioResponse])
def list_consultorios(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
) -> list[ConsultorioResponse]:
    return ConsultorioService(db).list(skip=skip, limit=limit)


@router.get("/{consultorio_id}", response_model=ConsultorioResponse)
def get_consultorio(consultorio_id: int, db: DbSession) -> ConsultorioResponse:
    return ConsultorioService(db).get(consultorio_id)


@router.put("/{consultorio_id}", response_model=ConsultorioResponse)
def update_consultorio(
    consultorio_id: int,
    payload: ConsultorioUpdate,
    db: DbSession,
) -> ConsultorioResponse:
    return ConsultorioService(db).update(consultorio_id, payload)


@router.delete("/{consultorio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consultorio(consultorio_id: int, db: DbSession) -> None:
    ConsultorioService(db).delete(consultorio_id)
