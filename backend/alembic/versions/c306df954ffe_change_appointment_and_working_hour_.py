"""change appointment and working hour types

Revision ID: c306df954ffe
Revises: 2794a8b8351c
Create Date: 2026-10-02 14:46:15.874474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c306df954ffe"
down_revision: Union[str, Sequence[str], None] = "2794a8b8351c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "Appointments",
        "appointment_date",
        existing_type=sa.String(length=10),
        type_=sa.Date(),
        existing_nullable=False,
        postgresql_using="appointment_date::date",
    )

    op.alter_column(
        "Appointments",
        "appointment_time",
        existing_type=sa.String(length=5),
        type_=sa.Time(),
        existing_nullable=False,
        postgresql_using="appointment_time::time",
    )

    op.alter_column(
        "professional_working_hours",
        "start_time",
        existing_type=sa.String(length=5),
        type_=sa.Time(),
        existing_nullable=False,
        postgresql_using="start_time::time",
    )

    op.alter_column(
        "professional_working_hours",
        "end_time",
        existing_type=sa.String(length=5),
        type_=sa.Time(),
        existing_nullable=False,
        postgresql_using="end_time::time",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "professional_working_hours",
        "end_time",
        existing_type=sa.Time(),
        type_=sa.String(length=5),
        existing_nullable=False,
        postgresql_using="to_char(end_time, 'HH24:MI')",
    )

    op.alter_column(
        "professional_working_hours",
        "start_time",
        existing_type=sa.Time(),
        type_=sa.String(length=5),
        existing_nullable=False,
        postgresql_using="to_char(start_time, 'HH24:MI')",
    )

    op.alter_column(
        "Appointments",
        "appointment_time",
        existing_type=sa.Time(),
        type_=sa.String(length=5),
        existing_nullable=False,
        postgresql_using="to_char(appointment_time, 'HH24:MI')",
    )

    op.alter_column(
        "Appointments",
        "appointment_date",
        existing_type=sa.Date(),
        type_=sa.String(length=10),
        existing_nullable=False,
        postgresql_using="appointment_date::text",
    )
