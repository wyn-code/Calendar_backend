"""Exportación de la planilla mensual de sesiones por paciente a PDF."""

from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.services.calendario_service import MESES
from app.services.planilla_pdf import FilaPlanilla, generar_planilla_pdf

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo_neurovital.png"
NOMBRE_PROFESIONAL = "Peralta Agustina"
OBRA_SOCIAL_DESCONOCIDA = "Obra Social"

logger = logging.getLogger(__name__)


class PlanillaPdfService:
    """Construye la planilla mensual de sesiones en PDF (una fila por paciente)."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AppointmentRepository(db)

    def build(self, year: int, month: int) -> BytesIO:
        """Genera el PDF y devuelve el buffer listo para StreamingResponse."""
        pdf_bytes = generar_planilla_pdf(
            filas=self._filas_del_mes(year, month),
            mes_nombre=MESES[month - 1],
            mes_y_anio_titulo=f"{MESES[month - 1]} {year}",
            nombre_profesional=NOMBRE_PROFESIONAL,
            logo_path=str(LOGO_PATH),
        )
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        return buffer

    def _filas_del_mes(self, year: int, month: int) -> list[FilaPlanilla]:
        """Agrupa los turnos del mes por paciente: una FilaPlanilla por paciente."""
        turnos_por_paciente: dict[int, list[Appointment]] = {}
        for appointment in self.repository.get_by_month(year, month):
            turnos_por_paciente.setdefault(appointment.patient.id, []).append(appointment)

        filas = []
        for turnos in turnos_por_paciente.values():
            paciente = turnos[0].patient
            turno = turnos[0]
            es_obra_social = turno.tipo_consulta.strip().lower() == "obra social"
            if es_obra_social:
                obra_social = turno.obra_social.nombre if turno.obra_social is not None else None
                if obra_social is None:
                    logger.warning(
                        "Turno %s (paciente %s) marcado como 'Obra Social' sin obra_social_id; "
                        "se muestra '%s' en la columna O.S.",
                        turno.id,
                        paciente.id,
                        OBRA_SOCIAL_DESCONOCIDA,
                    )
                    obra_social = OBRA_SOCIAL_DESCONOCIDA
            else:
                obra_social = None
            filas.append(
                FilaPlanilla(
                    paciente=paciente.nombre_completo,
                    obra_social=obra_social,
                    cantidad_sesiones=len(turnos),
                )
            )
        filas.sort(key=lambda fila: fila.paciente.lower())
        return filas
