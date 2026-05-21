"""phase 3 lead qualification

Revision ID: 002_phase_3_lead_qualification
Revises: 001_phase_1_crm_core
Create Date: 2026-05-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_phase_3_lead_qualification"
down_revision: Union[str, Sequence[str], None] = "001_phase_1_crm_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("qualification_intent", sa.String(length=64), nullable=True))
    op.add_column("leads", sa.Column("urgency", sa.String(length=32), nullable=True))
    op.add_column("leads", sa.Column("lead_score", sa.Integer(), nullable=True))
    op.add_column("leads", sa.Column("qualification_status", sa.String(length=64), nullable=True))
    op.add_column("leads", sa.Column("handover_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("leads", sa.Column("handover_reason", sa.String(length=120), nullable=True))
    op.add_column("leads", sa.Column("recommended_next_action", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("leads", "recommended_next_action")
    op.drop_column("leads", "handover_reason")
    op.drop_column("leads", "handover_required")
    op.drop_column("leads", "qualification_status")
    op.drop_column("leads", "lead_score")
    op.drop_column("leads", "urgency")
    op.drop_column("leads", "qualification_intent")
