from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Consultorio(str, Enum):
    """Consultorio al que pertenece el paciente."""

    NEUROVITAL = "Neurovital"
    INFANCIAS = "Infancias"


class Patient(Base):
    """Paciente perteneciente a un usuario."""

    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patients_consultorio_normalizado", "consultorio", "nombre_normalizado"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=True
    )
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_normalizado: Mapped[str] = mapped_column(
        String(200), nullable=False, server_default=""
    )
    consultorio: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=Consultorio.NEUROVITAL.value
    )
    telefono: Mapped[str | None] = mapped_column(String(50), nullable=True)
    obra_social_id: Mapped[int | None] = mapped_column(
        ForeignKey("obras_sociales.id"), nullable=True
    )
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="patients")
    obra_social: Mapped[ObraSocial | None] = relationship(back_populates="patients")
    appointments: Mapped[list[Appointment]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
