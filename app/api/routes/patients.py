from fastapi import APIRouter, status

from app.core.dependencies import DbSession
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: DbSession) -> PatientResponse:
    """Crea un nuevo paciente."""
    return PatientService(db).create(payload)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: DbSession) -> PatientResponse:
    """Devuelve un paciente por id."""
    return PatientService(db).get(patient_id)


@router.get("/", response_model=list[PatientResponse])
def list_patients(
    db: DbSession,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[PatientResponse]:
    """Lista pacientes paginados, con búsqueda opcional por nombre."""
    return PatientService(db).list(search=search, skip=skip, limit=limit)


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: DbSession,
) -> PatientResponse:
    """Actualiza un paciente."""
    return PatientService(db).update(patient_id, payload)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: DbSession) -> None:
    """Elimina un paciente."""
    PatientService(db).delete(patient_id)
