"""add tenant foundation to existing schema

Revision ID: a3d2d5d9c1b7
Revises: 768e9ffdb9d8
Create Date: 2026-06-13 00:00:00.000000
"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "a3d2d5d9c1b7"
down_revision: Union[str, None] = "768e9ffdb9d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_TENANT_SLUG = "default"
DEFAULT_TENANT_NAME = "Default Institution"
DEFAULT_TENANT_STATUS = "ACTIVE"
DEFAULT_TENANT_ID = uuid.uuid5(uuid.NAMESPACE_DNS, "safereport-map:default-tenant")

TARGET_TABLES = [
    "users",
    "reports",
    "clusters",
    "institution_areas",
    "ai_triage_results",
    "admin_notes",
    "report_status_history",
    "report_attachments",
    "audit_logs",
    "processing_jobs",
]


def _table_exists(insp: sa.Inspector, table_name: str) -> bool:
    return table_name in insp.get_table_names()


def _column_exists(insp: sa.Inspector, table_name: str, column_name: str) -> bool:
    if not _table_exists(insp, table_name):
        return False
    return any(col["name"] == column_name for col in insp.get_columns(table_name))


def _index_exists(insp: sa.Inspector, table_name: str, index_name: str) -> bool:
    if not _table_exists(insp, table_name):
        return False
    return any(idx["name"] == index_name for idx in insp.get_indexes(table_name))


def _fk_exists(insp: sa.Inspector, table_name: str, fk_name: str) -> bool:
    if not _table_exists(insp, table_name):
        return False
    return any(fk["name"] == fk_name for fk in insp.get_foreign_keys(table_name))


def _unique_exists(insp: sa.Inspector, table_name: str, uq_name: str) -> bool:
    if not _table_exists(insp, table_name):
        return False
    return any(uq["name"] == uq_name for uq in insp.get_unique_constraints(table_name))


def _backfill_tenant_id(bind, table_name: str, tenant_id: uuid.UUID) -> None:
    bind.execute(
        sa.text(f'UPDATE "{table_name}" SET tenant_id = :tenant_id WHERE tenant_id IS NULL'),
        {"tenant_id": str(tenant_id)},
    )


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=80), nullable=False, unique=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'ACTIVE'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("settings", JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    existing_tenant = bind.execute(
        sa.text("SELECT id FROM tenants WHERE slug = :slug"),
        {"slug": DEFAULT_TENANT_SLUG},
    ).scalar_one_or_none()

    if existing_tenant is None:
        bind.execute(
            sa.text(
                """
                INSERT INTO tenants (id, name, slug, status, is_active, settings, created_at, updated_at)
                VALUES (:id, :name, :slug, :status, :is_active, :settings, now(), now())
                """
            ),
            {
                "id": DEFAULT_TENANT_ID,
                "name": DEFAULT_TENANT_NAME,
                "slug": DEFAULT_TENANT_SLUG,
                "status": DEFAULT_TENANT_STATUS,
                "is_active": True,
                "settings": "{}",
            },
        )
        tenant_id = DEFAULT_TENANT_ID
    else:
        tenant_id = existing_tenant

    tenant_fk_type = UUID(as_uuid=True)

    for table_name in TARGET_TABLES:
        if not _table_exists(insp, table_name):
            continue

        column_name = "tenant_id"
        fk_name = f"fk_{table_name}_tenant_id_tenants"
        index_name = f"ix_{table_name}_tenant_id"

        if not _column_exists(insp, table_name, column_name):
            op.add_column(
                table_name,
                sa.Column(column_name, tenant_fk_type, nullable=True),
            )

        _backfill_tenant_id(bind, table_name, tenant_id)

        if table_name == "users":
            if _unique_exists(insp, table_name, "users_email_key"):
                op.drop_constraint("users_email_key", table_name, type_="unique")
            if not _unique_exists(insp, table_name, "uq_users_tenant_id_email"):
                op.create_unique_constraint("uq_users_tenant_id_email", table_name, ["tenant_id", "email"])

        if table_name == "institution_areas":
            if _unique_exists(insp, table_name, "institution_areas_code_key"):
                op.drop_constraint("institution_areas_code_key", table_name, type_="unique")
            if not _unique_exists(insp, table_name, "uq_institution_areas_tenant_id_code"):
                op.create_unique_constraint(
                    "uq_institution_areas_tenant_id_code",
                    table_name,
                    ["tenant_id", "code"],
                )

        if not _index_exists(insp, table_name, index_name):
            op.create_index(index_name, table_name, [column_name], unique=False)

        if not _fk_exists(insp, table_name, fk_name):
            op.create_foreign_key(
                fk_name,
                table_name,
                "tenants",
                [column_name],
                ["id"],
                ondelete="CASCADE",
            )

        op.alter_column(
            table_name,
            column_name,
            existing_type=tenant_fk_type,
            nullable=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    for table_name in reversed(TARGET_TABLES):
        if not _table_exists(insp, table_name):
            continue

        column_name = "tenant_id"
        fk_name = f"fk_{table_name}_tenant_id_tenants"
        index_name = f"ix_{table_name}_tenant_id"

        if table_name == "users":
            if _unique_exists(insp, table_name, "uq_users_tenant_id_email"):
                op.drop_constraint("uq_users_tenant_id_email", table_name, type_="unique")
            if not _unique_exists(insp, table_name, "users_email_key"):
                op.create_unique_constraint("users_email_key", table_name, ["email"])

        if table_name == "institution_areas":
            if _unique_exists(insp, table_name, "uq_institution_areas_tenant_id_code"):
                op.drop_constraint("uq_institution_areas_tenant_id_code", table_name, type_="unique")
            if not _unique_exists(insp, table_name, "institution_areas_code_key"):
                op.create_unique_constraint("institution_areas_code_key", table_name, ["code"])

        if _index_exists(insp, table_name, index_name):
            try:
                op.drop_index(index_name, table_name=table_name)
            except Exception:
                pass

        if _fk_exists(insp, table_name, fk_name):
            try:
                op.drop_constraint(fk_name, table_name, type_="foreignkey")
            except Exception:
                pass

        if _column_exists(insp, table_name, column_name):
            op.drop_column(table_name, column_name)

    op.drop_table("tenants")