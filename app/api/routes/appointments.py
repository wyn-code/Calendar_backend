from fastapi import APIRouter, status

from app.core.dependencies import DbSession
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: DbSession) -> AppointmentResponse:
    """Crea un nuevo turno."""
    return AppointmentService(db).create(payload)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: DbSession) -> AppointmentResponse:
    """Devuelve un turno por id."""
    return AppointmentService(db).get(appointment_id)


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
) -> list[AppointmentResponse]:
    """Lista turnos paginados."""
    return AppointmentService(db).list(skip=skip, limit=limit)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: DbSession,
) -> AppointmentResponse:
    """Actualiza un turno."""
    return AppointmentService(db).update(appointment_id, payload)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: DbSession) -> None:
    """Elimina un turno."""
    AppointmentService(db).delete(appointment_id)
