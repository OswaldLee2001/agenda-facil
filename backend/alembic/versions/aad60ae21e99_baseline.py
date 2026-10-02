"""baseline

Revision ID: aad60ae21e99
Revises:
Create Date: 2026-09-29 20:34:58.506146
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "aad60ae21e99"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial database schema."""

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_services_id",
        "services",
        ["id"],
        unique=False,
    )

    op.create_table(
        "professionals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_index(
        "ix_professionals_id",
        "professionals",
        ["id"],
        unique=False,
    )

    op.create_table(
        "Appointments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("professional_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("client_name", sa.String(length=100), nullable=False),
        sa.Column("client_phone", sa.String(length=20), nullable=False),
        sa.Column("appointment_date", sa.String(length=10), nullable=False),
        sa.Column("appointment_time", sa.String(length=5), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["professional_id"],
            ["professionals.id"],
            name="fk_appointments_professional",
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
            name="fk_appointments_service",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_Appointments_id",
        "Appointments",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial database schema."""

    op.drop_index(
        "ix_Appointments_id",
        table_name="Appointments",
    )
    op.drop_table("Appointments")

    op.drop_index(
        "ix_professionals_id",
        table_name="professionals",
    )
    op.drop_table("professionals")

    op.drop_index(
        "ix_services_id",
        table_name="services",
    )
    op.drop_table("services")
