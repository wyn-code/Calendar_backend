"""Modelos ORM. Se importan aquí para que Alembic detecte `Base.metadata`."""

from app.models.user import User
from app.models.patient import Patient
from app.models.obra_social import ObraSocial
from app.models.appointment import Appointment

__all__ = ["User", "Patient", "ObraSocial", "Appointment"]
