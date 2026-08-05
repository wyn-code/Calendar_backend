from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ObraSocial(Base):
    """Obra social con la que puede estar asociado un paciente."""

    __tablename__ = "obras_sociales"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    patients: Mapped[list[Patient]] = relationship(back_populates="obra_social")
    appointments: Mapped[list[Appointment]] = relationship(back_populates="obra_social")
