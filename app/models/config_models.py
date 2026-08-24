from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ConfigPrecio(Base):
    """Precio de sesión por tipo de consulta (singleton, una fila por key)."""

    __tablename__ = "config_precios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clave: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class ConfigPorcentaje(Base):
    """Porcentaje que se paga al consultorio por tipo de consulta."""

    __tablename__ = "config_porcentajes"
    __table_args__ = (
        UniqueConstraint("clave", "consultorio", name="uq_config_porcentajes_clave_consultorio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clave: Mapped[str] = mapped_column(String(50), nullable=False)
    consultorio: Mapped[str | None] = mapped_column(String(50), nullable=True)
    valor: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Factura(Base):
    """Factura cargada por la psicóloga."""

    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    paciente_nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    consultorio: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str | None] = mapped_column(String(20), nullable=True)
    obra_social: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nro_afiliado: Mapped[str | None] = mapped_column(String(50), nullable=True)
    periodo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fecha_emision: Mapped[str | None] = mapped_column(String(10), nullable=True)
    nro_factura: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sesiones: Mapped[int] = mapped_column(nullable=False, server_default="0")
    monto: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    porcentaje: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_pago: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
