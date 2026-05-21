"""phase 1 crm core

Revision ID: 001_phase_1_crm_core
Revises: None
Create Date: 2026-05-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_phase_1_crm_core"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_queue", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_departments_name", "departments", ["name"])

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.Column("department_id", sa.String(length=36), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("source_channel", sa.String(length=64), nullable=True),
        sa.Column("consent_status", sa.String(length=64), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_phone", "customers", ["phone"])
    op.create_index("ix_customers_email", "customers", ["email"])

    op.create_table(
        "pipelines",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("department_id", sa.String(length=36), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pipeline_stages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("pipeline_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False),
        sa.Column("is_lost", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipeline_stages_pipeline_id", "pipeline_stages", ["pipeline_id"])

    op.create_table(
        "leads",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("interest_area", sa.String(length=255), nullable=True),
        sa.Column("program", sa.String(length=255), nullable=True),
        sa.Column("department_id", sa.String(length=36), nullable=True),
        sa.Column("assigned_user_id", sa.String(length=36), nullable=True),
        sa.Column("stage_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.String(length=64), nullable=False),
        sa.Column("source_channel", sa.String(length=64), nullable=True),
        sa.Column("source_domain", sa.String(length=255), nullable=True),
        sa.Column("campaign_tag", sa.String(length=255), nullable=True),
        sa.Column("is_international_priority", sa.Boolean(), nullable=False),
        sa.Column("medical_track", sa.Boolean(), nullable=False),
        sa.Column("intake_period", sa.String(length=64), nullable=True),
        sa.Column("relocation_needed", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["assigned_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["stage_id"], ["pipeline_stages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leads_customer_id", "leads", ["customer_id"])

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("ai_handled", sa.Boolean(), nullable=False),
        sa.Column("human_handover", sa.Boolean(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_customer_id", "conversations", ["customer_id"])
    op.create_index("ix_conversations_lead_id", "conversations", ["lead_id"])

    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("sender_type", sa.String(length=64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("channel_message_id", sa.String(length=255), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("customer_id", sa.String(length=36), nullable=True),
        sa.Column("assigned_user_id", sa.String(length=36), nullable=True),
        sa.Column("department_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("priority", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["assigned_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_customer_id", "tasks", ["customer_id"])
    op.create_index("ix_tasks_lead_id", "tasks", ["lead_id"])

    op.create_table(
        "lead_stage_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("lead_id", sa.String(length=36), nullable=False),
        sa.Column("from_stage_id", sa.String(length=36), nullable=True),
        sa.Column("to_stage_id", sa.String(length=36), nullable=True),
        sa.Column("changed_by", sa.String(length=36), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["from_stage_id"], ["pipeline_stages.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"]),
        sa.ForeignKeyConstraint(["to_stage_id"], ["pipeline_stages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_stage_history_lead_id", "lead_stage_history", ["lead_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

    op.create_table(
        "deadline_tracking",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("deadline_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("deadline_date", sa.Date(), nullable=False),
        sa.Column("program", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("deadline_tracking")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_lead_stage_history_lead_id", table_name="lead_stage_history")
    op.drop_table("lead_stage_history")
    op.drop_index("ix_tasks_lead_id", table_name="tasks")
    op.drop_index("ix_tasks_customer_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_messages_conversation_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_conversations_lead_id", table_name="conversations")
    op.drop_index("ix_conversations_customer_id", table_name="conversations")
    op.drop_table("conversations")
    op.drop_index("ix_leads_customer_id", table_name="leads")
    op.drop_table("leads")
    op.drop_index("ix_pipeline_stages_pipeline_id", table_name="pipeline_stages")
    op.drop_table("pipeline_stages")
    op.drop_table("pipelines")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_index("ix_customers_phone", table_name="customers")
    op.drop_table("customers")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_departments_name", table_name="departments")
    op.drop_table("departments")
