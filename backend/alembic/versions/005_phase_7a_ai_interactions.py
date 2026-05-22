"""phase 7a ai interactions

Revision ID: 005_phase_7a_ai_interactions
Revises: 004_phase_5c_auth_security
Create Date: 2026-05-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005_phase_7a_ai_interactions"
down_revision: Union[str, Sequence[str], None] = "004_phase_5c_auth_security"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_interactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("message_id", sa.String(length=36), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("intent", sa.String(length=120), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("sources_json", sa.JSON(), nullable=True),
        sa.Column("flags_json", sa.JSON(), nullable=True),
        sa.Column("raw_response_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_interactions_conversation_id", "ai_interactions", ["conversation_id"])
    op.create_index("ix_ai_interactions_message_id", "ai_interactions", ["message_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_interactions_message_id", table_name="ai_interactions")
    op.drop_index("ix_ai_interactions_conversation_id", table_name="ai_interactions")
    op.drop_table("ai_interactions")

