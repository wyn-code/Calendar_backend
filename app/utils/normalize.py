"""Normalización de nombres de pacientes para detección de duplicados."""

from __future__ import annotations

import unicodedata


def normalize_nombre(nombre: str) -> str:
    """Normaliza un nombre para comparar/agrupar.

    Resultado: tokens en minúscula, sin tildes y ordenados alfabéticamente.
    Ej: "Juan Pérez" y "Pérez Juan" → "juan perez".
    Mantiene el campo original (`nombre_completo`) intacto para mostrarlo.
    """
    sin_tildes = unicodedata.normalize("NFD", nombre)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    tokens = [t for t in sin_tildes.lower().split() if t]
    return " ".join(sorted(tokens))
