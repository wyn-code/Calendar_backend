import logging
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.patient import Consultorio, Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientCreate, PatientUpdate
from app.utils.normalize import normalize_nombre

logger = logging.getLogger(__name__)


class PatientService:
    """Lógica de negocio de pacientes."""

    def __init__(self, db: Session) -> None:
        self.repository = PatientRepository(db)

    def create(self, data: PatientCreate) -> Patient:
        """Crea un nuevo paciente.

        Rechaza con 409 si ya existe otro paciente del mismo consultorio con
        el mismo nombre normalizado (evita duplicados por orden de nombre).
        """
        payload = data.model_dump()
        payload["nombre_normalizado"] = normalize_nombre(data.nombre_completo)
        existing = self.repository.get_duplicate(
            payload["nombre_normalizado"], payload["consultorio"]
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Ya existe un paciente similar.",
                    "existing_patient_id": existing.id,
                    "existing_nombre": existing.nombre_completo,
                },
            )
        patient = self.repository.create(payload)
        self._create_factura_folder(patient.id)
        return patient

    def _create_factura_folder(self, patient_id: int) -> None:
        """Crea la carpeta de facturas para un paciente. Best-effort: no falla si no puede."""
        try:
            base = Path(settings.FACTURAS_BASE_PATH)
            folder = base / str(patient_id)
            folder.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.warning(
                "No se pudo crear la carpeta de facturas para el paciente %s", patient_id
            )

    def update(self, obj_id: int, data: PatientUpdate) -> Patient:
        """Actualiza un paciente existente."""
        instance = self.get(obj_id)
        updates = data.model_dump(exclude_unset=True)
        if "nombre_completo" in updates:
            updates["nombre_normalizado"] = normalize_nombre(
                updates["nombre_completo"]
            )
        self._check_duplicate_on_update(instance, updates)
        return self.repository.update(instance, updates)

    def _check_duplicate_on_update(self, instance: Patient, updates: dict) -> None:
        """Rechaza con 409 si la actualización genera un duplicado dentro del consultorio."""
        consultorio = updates.get("consultorio", instance.consultorio)
        if isinstance(consultorio, Consultorio):
            consultorio = consultorio.value
        nombre_normalizado = updates.get(
            "nombre_normalizado", instance.nombre_normalizado
        )
        existing = self.repository.get_duplicate(nombre_normalizado, consultorio)
        if existing is not None and existing.id != instance.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Ya existe un paciente similar.",
                    "existing_patient_id": existing.id,
                    "existing_nombre": existing.nombre_completo,
                },
            )

    def delete(self, obj_id: int) -> None:
        """Elimina un paciente."""
        instance = self.get(obj_id)
        self.repository.delete(instance)

    def get(self, obj_id: int) -> Patient:
        """Devuelve un paciente por id."""
        instance = self.repository.get_by_id(obj_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
            )
        return instance

    def list(
        self,
        *,
        search: str | None = None,
        consultorio: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Patient]:
        """Devuelve una lista paginada de pacientes, con búsqueda por nombre."""
        return self.repository.get_all(
            search=search, consultorio=consultorio, skip=skip, limit=limit
        )
