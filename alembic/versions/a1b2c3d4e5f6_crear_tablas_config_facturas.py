"""crear tablas consultorios, config_precios, config_porcentajes, facturas

Revision ID: a1b2c3d4e5f6
Revises: f3a7b9c1d2e4
Create Date: 2026-08-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f3a7b9c1d2e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- consultorios ---
    op.create_table(
        'consultorios',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('nombre', sa.String(length=100), unique=True, nullable=False),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Insertar los 2 consultorios que ya existen como enum
    op.execute("INSERT INTO consultorios (nombre) VALUES ('Neurovital'), ('Infancias')")

    # --- config_precios ---
    op.create_table(
        'config_precios',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('clave', sa.String(length=50), unique=True, nullable=False),
        sa.Column('valor', sa.Float(), server_default='0', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- config_porcentajes ---
    op.create_table(
        'config_porcentajes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('clave', sa.String(length=50), unique=True, nullable=False),
        sa.Column('valor', sa.Float(), server_default='0', nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- facturas ---
    op.create_table(
        'facturas',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('paciente_nombre', sa.String(length=200), nullable=False),
        sa.Column('consultorio', sa.String(length=100), nullable=False),
        sa.Column('dni', sa.String(length=20), nullable=True),
        sa.Column('obra_social', sa.String(length=100), nullable=True),
        sa.Column('nro_afiliado', sa.String(length=50), nullable=True),
        sa.Column('periodo', sa.String(length=50), nullable=True),
        sa.Column('fecha_emision', sa.String(length=10), nullable=True),
        sa.Column('nro_factura', sa.String(length=50), nullable=True),
        sa.Column('sesiones', sa.Integer(), server_default='0', nullable=False),
        sa.Column('monto', sa.Float(), server_default='0', nullable=False),
        sa.Column('porcentaje', sa.Float(), nullable=True),
        sa.Column('fecha_pago', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('facturas')
    op.drop_table('config_porcentajes')
    op.drop_table('config_precios')
    op.drop_table('consultorios')
