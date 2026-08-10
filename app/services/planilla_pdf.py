"""
planilla_pdf.py

Genera la planilla mensual de sesiones (PACIENTE / O.S. / PARTICULAR /
CANT. SESIONES / MES COBRADO) en PDF vertical, con logo y nombre del
profesional en el encabezado.

Pensado para conectarse directo a un endpoint de FastAPI: la función
generar_planilla_pdf() devuelve los bytes del PDF, listos para mandar
en una StreamingResponse.

Uso típico desde el backend:

    from planilla_pdf import generar_planilla_pdf, FilaPlanilla

    filas = [
        FilaPlanilla(paciente="Batippede Pedro", obra_social=None, cantidad_sesiones=3),
        FilaPlanilla(paciente="Tevez Milena", obra_social="IOMA", cantidad_sesiones=8),
        ...
    ]

    pdf_bytes = generar_planilla_pdf(
        filas=filas,
        mes_nombre="Agosto",
        mes_y_anio_titulo="Agosto 2026",
        nombre_profesional="Peralta Agustina",
        logo_path="assets/logo_neurovital.png",
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="planilla-sesiones-agosto-2026.pdf"'},
    )
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Iterable, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.graphics.shapes import Drawing, Polygon


# ----------------------------------------------------------------------
# Modelo de datos de entrada
# ----------------------------------------------------------------------
@dataclass
class FilaPlanilla:
    paciente: str                       # nombre y apellido completo
    obra_social: Optional[str]          # None o "" = paciente particular
    cantidad_sesiones: int              # turnos del paciente en el mes

    @property
    def es_particular(self) -> bool:
        return not self.obra_social


# ----------------------------------------------------------------------
# Helper: check vectorial (no depender del glyph Unicode ✔, que Helvetica
# no soporta y en varios lectores de PDF no se ve)
# ----------------------------------------------------------------------
def _crear_check(size: float = 10, color=colors.HexColor("#2E7D32")) -> Drawing:
    d = Drawing(size, size)
    puntos = [
        size * 0.02, size * 0.42,
        size * 0.38, size * 0.05,
        size * 0.38, size * 0.30,
        size * 0.98, size * 0.75,
        size * 0.90, size * 0.98,
        size * 0.35, size * 0.62,
    ]
    d.add(Polygon(puntos, fillColor=color, strokeColor=color, strokeWidth=0.5))
    return d


# ----------------------------------------------------------------------
# Función principal
# ----------------------------------------------------------------------
def generar_planilla_pdf(
    filas: Iterable[FilaPlanilla],
    mes_nombre: str,
    mes_y_anio_titulo: str,
    nombre_profesional: str,
    logo_path: str,
    filas_vacias_extra: int = 10,
) -> bytes:
    """
    Arma el PDF de la planilla de sesiones y devuelve los bytes listos
    para servir en una respuesta HTTP o guardar en disco.

    filas: lista de FilaPlanilla con los datos reales del mes (uno por
        paciente, ya agrupados/contados desde la base).
    mes_nombre: valor que va en la columna "MES COBRADO" (ej. "Agosto").
    mes_y_anio_titulo: valor que va en el título de la planilla
        (ej. "Agosto 2026").
    nombre_profesional: nombre que aparece arriba a la derecha.
    logo_path: path al logo (imagen) que va arriba a la izquierda.
    filas_vacias_extra: cantidad de filas en blanco a agregar al final
        de la tabla, por prolijidad visual. 0 para no agregar ninguna.
    """
    filas = list(filas)

    styles = getSampleStyleSheet()
    style_nombre_dr = ParagraphStyle(
        "NombreDr", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=15, alignment=TA_RIGHT, textColor=colors.HexColor("#2B2B2B"),
    )
    style_titulo = ParagraphStyle(
        "Titulo", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=13, alignment=TA_LEFT, textColor=colors.HexColor("#2B2B2B"),
        spaceBefore=4, spaceAfter=14,
    )
    style_celda_left = ParagraphStyle(
        "CeldaIzq", parent=styles["Normal"], fontName="Helvetica",
        fontSize=9.5, leading=11, alignment=TA_LEFT,
    )
    style_celda_center = ParagraphStyle(
        "CeldaCentro", parent=styles["Normal"], fontName="Helvetica",
        fontSize=9.5, leading=11, alignment=TA_CENTER,
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=16 * mm, rightMargin=16 * mm,
    )

    story = []

    # --- Encabezado: logo a la izquierda, nombre del profesional a la derecha ---
    logo = Image(logo_path, width=22 * mm, height=20.7 * mm)
    header_tbl = Table(
        [[logo, Paragraph(nombre_profesional, style_nombre_dr)]],
        colWidths=[100 * mm, None],
    )
    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 10 * mm))

    # --- Título del mes ---
    story.append(Paragraph(f"Planilla de sesiones — {mes_y_anio_titulo}", style_titulo))

    # --- Tabla principal ---
    encabezado = ["PACIENTE", "O.S.", "PARTICULAR", "CANT.\nSESIONES", "MES\nCOBRADO"]
    data = [encabezado]
    for f in filas:
        data.append([
            Paragraph(f.paciente, style_celda_left),
            Paragraph(f.obra_social if f.obra_social else "-", style_celda_center),
            _crear_check() if f.es_particular else Paragraph("-", style_celda_center),
            str(f.cantidad_sesiones),
            mes_nombre,
        ])

    for _ in range(filas_vacias_extra):
        data.append(["", "", "", "", ""])

    col_widths = [52 * mm, 26 * mm, 26 * mm, 26 * mm, 26 * mm]
    tabla = Table(data, colWidths=col_widths, repeatRows=1)

    n_filas_con_datos = len(filas)
    tabla.setStyle(TableStyle([
        # encabezado
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),

        # cuerpo
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (0, -1), 6),

        # bordes (filas con datos más marcadas, filas vacías más tenues)
        ("GRID", (0, 0), (-1, n_filas_con_datos), 0.6, colors.HexColor("#8A8A8A")),
        ("GRID", (0, n_filas_con_datos + 1), (-1, -1), 0.6, colors.HexColor("#C9C9C9")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#5A5A5A")),
    ]))

    story.append(tabla)
    doc.build(story)

    return buffer.getvalue()


# ----------------------------------------------------------------------
# Ejemplo de uso local (genera un archivo con la tabla vacía, sin datos,
# solo para verificar visualmente el template antes de conectarlo)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    pdf_bytes = generar_planilla_pdf(
        filas=[],  # sin datos todavía: se conecta más adelante a la consulta real
        mes_nombre="Agosto",
        mes_y_anio_titulo="Agosto 2026",
        nombre_profesional="Peralta Agustina",
        logo_path="logo_neurovital.png",
        filas_vacias_extra=18,
    )
    with open("planilla-sesiones-vacia.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("Listo: planilla-sesiones-vacia.pdf")
