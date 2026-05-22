"""phase 7b knowledge governance metadata

Revision ID: 006_phase_7b_knowledge_governance
Revises: 005_phase_7a_ai_interactions
Create Date: 2026-05-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "006_phase_7b_knowledge_governance"
down_revision: Union[str, Sequence[str], None] = "005_phase_7a_ai_interactions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("knowledge_sources", sa.Column("source_key", sa.String(length=160), nullable=True))
    op.add_column("knowledge_sources", sa.Column("source_domain", sa.String(length=255), nullable=True))
    op.add_column("knowledge_sources", sa.Column("category", sa.String(length=120), nullable=True))
    op.add_column("knowledge_sources", sa.Column("sensitivity", sa.String(length=32), nullable=True))
    op.add_column("knowledge_sources", sa.Column("review_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("knowledge_sources", sa.Column("stale_after_days", sa.Integer(), nullable=True))
    op.create_index("ix_knowledge_sources_source_key", "knowledge_sources", ["source_key"])
    op.create_index("ix_knowledge_sources_source_domain", "knowledge_sources", ["source_domain"])
    op.create_index("ix_knowledge_sources_category", "knowledge_sources", ["category"])

    op.add_column("knowledge_snippets", sa.Column("source_key", sa.String(length=160), nullable=True))
    op.add_column("knowledge_snippets", sa.Column("source_domain", sa.String(length=255), nullable=True))
    op.add_column("knowledge_snippets", sa.Column("sensitivity", sa.String(length=32), nullable=True))
    op.add_column("knowledge_snippets", sa.Column("review_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("knowledge_snippets", sa.Column("stale_after_days", sa.Integer(), nullable=True))
    op.add_column("knowledge_snippets", sa.Column("content_hash", sa.String(length=64), nullable=True))
    op.create_index("ix_knowledge_snippets_source_key", "knowledge_snippets", ["source_key"])
    op.create_index("ix_knowledge_snippets_source_domain", "knowledge_snippets", ["source_domain"])
    op.create_index("ix_knowledge_snippets_content_hash", "knowledge_snippets", ["content_hash"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_snippets_content_hash", table_name="knowledge_snippets")
    op.drop_index("ix_knowledge_snippets_source_domain", table_name="knowledge_snippets")
    op.drop_index("ix_knowledge_snippets_source_key", table_name="knowledge_snippets")
    op.drop_column("knowledge_snippets", "content_hash")
    op.drop_column("knowledge_snippets", "stale_after_days")
    op.drop_column("knowledge_snippets", "review_required")
    op.drop_column("knowledge_snippets", "sensitivity")
    op.drop_column("knowledge_snippets", "source_domain")
    op.drop_column("knowledge_snippets", "source_key")

    op.drop_index("ix_knowledge_sources_category", table_name="knowledge_sources")
    op.drop_index("ix_knowledge_sources_source_domain", table_name="knowledge_sources")
    op.drop_index("ix_knowledge_sources_source_key", table_name="knowledge_sources")
    op.drop_column("knowledge_sources", "stale_after_days")
    op.drop_column("knowledge_sources", "review_required")
    op.drop_column("knowledge_sources", "sensitivity")
    op.drop_column("knowledge_sources", "category")
    op.drop_column("knowledge_sources", "source_domain")
    op.drop_column("knowledge_sources", "source_key")
