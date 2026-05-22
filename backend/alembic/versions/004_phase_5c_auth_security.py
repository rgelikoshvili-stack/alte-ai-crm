"""phase 5c auth security

Revision ID: 004_phase_5c_auth_security
Revises: 003_phase_4_knowledge_base
Create Date: 2026-05-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "004_phase_5c_auth_security"
down_revision: Union[str, Sequence[str], None] = "003_phase_4_knowledge_base"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_hash")

