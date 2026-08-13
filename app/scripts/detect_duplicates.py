"""Detección (y fusión manual) de pacientes duplicados por nombre normalizado.

Uso:
    python -m app.scripts.detect_duplicates                    # genera reporte
    python -m app.scripts.detect_duplicates --merge 5 6 7      # re-encamina turnos
                                                               # de 6 y 7 hacia 5 y borra
                                                               # los pacientes 6 y 7

NO fusiona nada automáticamente: el modo --merge solo corre con la lista
explícita de ids después de revisar el reporte generado manualmente.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime

from sqlalchemy import func, select, update

from app.core.database import SessionLocal
from app.models.appointment import Appointment
from app.models.patient import Patient

REPORT_PATH = "duplicates_report.json"


def _turnos_paciente(db, patient_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Appointment)
        .where(Appointment.patient_id == patient_id)
    )
    return int(db.scalar(stmt) or 0)


def build_report(db) -> list[dict]:
    """Agrupa pacientes por nombre_normalizado y arma una lista de grupos duplicados."""
    pacientes = list(db.scalars(select(Patient).order_by(Patient.nombre_completo)))
    grupos: dict[str, list[Patient]] = {}
    for p in pacientes:
        grupos.setdefault(p.nombre_normalizado, []).append(p)

    report: list[dict] = []
    for norm, ps in sorted(grupos.items()):
        if len(ps) < 2:
            continue
        report.append(
            {
                "nombre_normalizado": norm,
                "cantidad_candidatos": len(ps),
                "candidatos": [
                    {
                        "id": p.id,
                        "nombre_completo": p.nombre_completo,
                        "consultorio": p.consultorio,
                        "telefono": p.telefono,
                        "turnos": _turnos_paciente(db, p.id),
                        "created_at": p.created_at.isoformat()
                        if isinstance(p.created_at, datetime)
                        else str(p.created_at),
                    }
                    for p in sorted(ps, key=lambda x: x.created_at or datetime.min)
                ],
            }
        )
    return report


def merge(db, target_id: int, orphan_ids: list[int]) -> None:
    """Re-encamina los turnos de `orphan_ids` hacia `target_id` y borra los huérfanos."""
    target = db.get(Patient, target_id)
    if target is None:
        raise SystemExit(f"El paciente target {target_id} no existe.")

    for pid in orphan_ids:
        if pid == target_id:
            print(f"Omitiendo {pid}: es el mismo que el target.")
            continue
        orphan = db.get(Patient, pid)
        if orphan is None:
            print(f"ADVERTENCIA: el paciente {pid} no existe; se omite.")
            continue
        movidos = db.execute(
            update(Appointment)
            .where(Appointment.patient_id == pid)
            .values(patient_id=target_id)
        ).rowcount
        db.delete(orphan)
        print(
            f"Paciente #{pid} '{orphan.nombre_completo}': {movidos} turnos "
            f"reasignados a #{target_id} '{target.nombre_completo}' y eliminado."
        )
    db.commit()
    print("Fusión completada. Revisá el calendario antes de borrar el reporte.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--merge",
        nargs="+",
        type=int,
        metavar="ID",
        help="ids a fusionar: el primero es el target, el resto se fusionan hacia él.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.merge:
            if len(args.merge) < 2:
                raise SystemExit("--merge requiere al menos 2 ids: target y los que se fusionan.")
            merge(db, args.merge[0], args.merge[1:])
            return

        report = build_report(db)
        total_duplicados = sum(g["cantidad_candidatos"] - 1 for g in report)
        print(f"Grupos con posibles duplicados: {len(report)}")
        print(f"Candidatos duplicados (sobre el primero de cada grupo): {total_duplicados}")
        for g in report:
            print(f"\n== {g['nombre_normalizado']} ({g['cantidad_candidatos']} candidatos) ==")
            for c in g["candidatos"]:
                print(
                    f"  #{c['id']:<5} {c['nombre_completo']:<40} "
                    f"{c['consultorio']:<10} turnos={c['turnos']} alta={c['created_at']}"
                )

        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nReporte completo guardado en {REPORT_PATH}")
        print("Revisalo y usá --merge <target> <duplicado...> solo si confirmás.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
