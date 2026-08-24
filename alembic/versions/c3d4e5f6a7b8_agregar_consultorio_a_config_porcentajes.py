"""agregar consultorio a config_porcentajes

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna consultorio (nullable para retrocompatibilidad)
    op.add_column('config_porcentajes', sa.Column('consultorio', sa.String(length=50), nullable=True))

    # Quitar la restricción unique existente en 'clave'
    op.drop_constraint('config_porcentajes_clave_key', 'config_porcentajes', type_='unique')

    # Crear restricción unique compuesta (clave + consultorio)
    op.create_unique_constraint(
        'uq_config_porcentajes_clave_consultorio',
        'config_porcentajes',
        ['clave', 'consultorio'],
    )

    # Migrar datos existentes: asignar los porcentajes actuales a todos los consultorios conocidos
    op.execute("""
        INSERT INTO config_porcentajes (clave, consultorio, valor)
        SELECT clave, c.nombre, cp.valor
        FROM config_porcentajes cp
        CROSS JOIN consultorios c
        WHERE cp.consultorio IS NULL
        ON CONFLICT DO NOTHING
    """)

    # Eliminar las filas legacy sin consultorio
    op.execute("DELETE FROM config_porcentajes WHERE consultorio IS NULL")


def downgrade() -> None:
    op.drop_constraint('uq_config_porcentajes_clave_consultorio', 'config_porcentajes', type_='unique')
    op.create_unique_constraint('config_porcentajes_clave_key', 'config_porcentajes', ['clave'])
    op.drop_column('config_porcentajes', 'consultorio')
