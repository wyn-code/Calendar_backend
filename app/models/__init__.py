"""Modelos ORM. Se importan aquí para que Alembic detecte `Base.metadata`."""

from app.models.user import User
from app.models.patient import Patient
from app.models.obra_social import ObraSocial
from app.models.appointment import Appointment
from app.models.consultorio import Consultorio
from app.models.config_models import ConfigPrecio, ConfigPorcentaje, Factura
from app.models.user_settings import UserSettings

__all__ = [
    "User",
    "Patient",
    "ObraSocial",
    "Appointment",
    "Consultorio",
    "ConfigPrecio",
    "ConfigPorcentaje",
    "Factura",
    "UserSettings",
]
