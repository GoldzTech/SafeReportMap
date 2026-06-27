"""initial schema

Revision ID: 768e9ffdb9d8
Revises:
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "768e9ffdb9d8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


report_status_enum = sa.Enum(
    "RECEIVED",
    "IN_REVIEW",
    "FORWARDED",
    "RESOLVED",
    "ARCHIVED",
    name="report_status",
)

severity_level_enum = sa.Enum(
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
    name="severity_level",
)

incident_category_enum = sa.Enum(
    "VERBAL_HARASSMENT",
    "DISCRIMINATION",
    "INTIMIDATION",
    "EXCLUSION",
    "THREAT",
    "INAPPROPRIATE_PHYSICAL_CONTACT",
    "OTHER",
    name="incident_category",
)

user_role_enum = sa.Enum(
    "ADMIN",
    "GESTOR",
    name="user_role",
)

cluster_type_enum = sa.Enum(
    "TEXTUAL",
    "SPATIAL",
    "TEMPORAL",
    "HYBRID",
    name="cluster_type",
)

job_status_enum = sa.Enum(
    "PENDING",
    "RUNNING",
    "SUCCESS",
    "FAILED",
    "RETRYING",
    name="job_status",
)


def upgrade() -> None:
    op.create_table(
        "institution_areas",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True, unique=True),
        sa.Column("area_type", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "clusters",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("cluster_type", cluster_type_enum, nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("severity_level", severity_level_enum, nullable=True),
        sa.Column("recurrence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("zone_reference", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("incident_date", sa.Date(), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=False),
        sa.Column("location_zone", sa.String(length=120), nullable=True),
        sa.Column(
            "institution_area_id",
            UUID(as_uuid=True),
            sa.ForeignKey("institution_areas.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("content_raw", sa.Text(), nullable=False),
        sa.Column("content_sanitized", sa.Text(), nullable=False),
        sa.Column("urgency_self_reported", sa.SmallInteger(), nullable=True),
        sa.Column("status", report_status_enum, nullable=False),
        sa.Column("recurrence_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "cluster_id",
            UUID(as_uuid=True),
            sa.ForeignKey("clusters.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("submitted_from_demo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("public_reference_code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "report_attachments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "report_id",
            UUID(as_uuid=True),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "ai_triage_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "report_id",
            UUID(as_uuid=True),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", incident_category_enum, nullable=False),
        sa.Column("severity", severity_level_enum, nullable=False),
        sa.Column("priority_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("keywords", JSONB, nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("recurrence_score", sa.Float(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("model_version", sa.String(length=80), nullable=False),
        sa.Column("pipeline_version", sa.String(length=80), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "processing_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "report_id",
            UUID(as_uuid=True),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", job_status_enum, nullable=False),
        sa.Column("attempt_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "admin_notes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "report_id",
            UUID(as_uuid=True),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "admin_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "report_status_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "report_id",
            UUID(as_uuid=True),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("previous_status", report_status_enum, nullable=True),
        sa.Column("new_status", report_status_enum, nullable=False),
        sa.Column(
            "changed_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "actor_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=False),
        sa.Column("target_id", UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("ip_hash", sa.String(length=128), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("report_status_history")
    op.drop_table("admin_notes")
    op.drop_table("processing_jobs")
    op.drop_table("ai_triage_results")
    op.drop_table("report_attachments")
    op.drop_table("reports")
    op.drop_table("users")
    op.drop_table("clusters")
    op.drop_table("institution_areas")

    bind = op.get_bind()
    job_status_enum.drop(bind, checkfirst=True)
    cluster_type_enum.drop(bind, checkfirst=True)
    user_role_enum.drop(bind, checkfirst=True)
    incident_category_enum.drop(bind, checkfirst=True)
    severity_level_enum.drop(bind, checkfirst=True)
    report_status_enum.drop(bind, checkfirst=True)