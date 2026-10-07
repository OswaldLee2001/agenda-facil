"""add role to users

Revision ID: 89740733737a
Revises: 27e87660ed01
Create Date: 2026-10-06 20:57:01.581422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "89740733737a"
down_revision: Union[str, Sequence[str], None] = "27e87660ed01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="client",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")
