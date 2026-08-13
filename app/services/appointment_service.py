from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.patient import Consultorio, Patient
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.patient_repository import PatientRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.utils.normalize import normalize_nombre

DEFAULT_CONSULTORIO = Consultorio.NEUROVITAL.value


class AppointmentService:
    """Lógica de negocio de turnos."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AppointmentRepository(db)
        self.patient_repository = PatientRepository(db)

    def create(self, data: AppointmentCreate) -> Appointment:
        """Crea un nuevo turno, reutilizando o creando el paciente asociado."""
        patient_id = self._resolve_patient_id(data)
        payload = data.model_dump(exclude={"nombre_completo", "consultorio"})
        payload["patient_id"] = patient_id
        return self.repository.create(payload)

    def _resolve_patient_id(self, data: AppointmentCreate) -> int:
        """Devuelve el id de paciente a usar, reutilizando o creando si hace falta."""
        if data.patient_id is not None:
            if self.patient_repository.get_by_id(data.patient_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
                )
            return data.patient_id
        return self._find_or_create_patient(data.nombre_completo, data.consultorio)

    def _find_or_create_patient(
        self, nombre_completo: str, consultorio: str | None = None
    ) -> int:
        """Reutiliza un paciente existente por nombre normalizado o crea uno nuevo.

        Solo compara dentro del mismo consultorio para no cruzar pacientes
        entre Neurovital e Infancias.
        """
        consultorio = consultorio or DEFAULT_CONSULTORIO
        if isinstance(consultorio, Consultorio):
            consultorio = consultorio.value
        normalized = normalize_nombre(nombre_completo)
        existing = self.patient_repository.get_duplicate(normalized, consultorio)
        if existing is not None:
            return existing.id

        patient = Patient(
            nombre_completo=nombre_completo,
            nombre_normalizado=normalized,
            consultorio=consultorio,
        )
        self.db.add(patient)
        self.db.flush()
        return patient.id

    def update(self, obj_id: int, data: AppointmentUpdate) -> Appointment:
        """Actualiza un turno existente."""
        instance = self.get(obj_id)
        updates = self._resolve_patient_updates(data.model_dump(exclude_unset=True))
        return self.repository.update(instance, updates)

    def _resolve_patient_updates(self, updates: dict) -> dict:
        """Reasigna el paciente del turno según patient_id o nombre_completo."""
        updates = dict(updates)
        patient_id = updates.pop("patient_id", None)
        nombre_completo = updates.pop("nombre_completo", None)
        consultorio = updates.pop("consultorio", None)

        if patient_id is not None:
            if self.patient_repository.get_by_id(patient_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
                )
            updates["patient_id"] = patient_id
        elif nombre_completo is not None:
            updates["patient_id"] = self._find_or_create_patient(
                nombre_completo, consultorio
            )
        return updates

    def delete(self, obj_id: int) -> None:
        """Elimina un turno."""
        instance = self.get(obj_id)
        self.repository.delete(instance)

    def get(self, obj_id: int) -> Appointment:
        """Devuelve un turno por id."""
        instance = self.repository.get_by_id(obj_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Turno no encontrado"
            )
        return instance

    def list(self, *, skip: int = 0, limit: int = 100) -> list[Appointment]:
        """Devuelve una lista paginada de turnos."""
        return self.repository.get_all(skip=skip, limit=limit)
