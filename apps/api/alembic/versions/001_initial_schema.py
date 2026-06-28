"""Initial ASL schema — Phase 0."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "policy_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("version", sa.String(32), nullable=False, unique=True),
        sa.Column("document", postgresql.JSONB(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(128)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index(
        "uq_policy_versions_single_active",
        "policy_versions",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    op.create_table(
        "decision_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("decision_id", sa.String(32), nullable=False, unique=True),
        sa.Column("session_id", sa.String(128), nullable=False),
        sa.Column("agent_id", sa.String(128), nullable=False),
        sa.Column("tool", sa.String(256), nullable=False),
        sa.Column("arguments_redacted", postgresql.JSONB(), nullable=False),
        sa.Column("arguments_hash", sa.String(64), nullable=False),
        sa.Column("risk_tier", sa.String(16), nullable=False),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("final_outcome", sa.String(16), nullable=True),
        sa.Column("reason_code", sa.String(64), nullable=False),
        sa.Column(
            "policy_version",
            sa.String(32),
            sa.ForeignKey("policy_versions.version"),
            nullable=False,
        ),
        sa.Column("principal", postgresql.JSONB(), nullable=False),
        sa.Column(
            "delegation_chain",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("idempotency_key", sa.String(128), unique=True, nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_decision_records_session_created", "decision_records", ["session_id", "created_at"])
    op.create_index("ix_decision_records_agent_created", "decision_records", ["agent_id", "created_at"])
    op.create_index(
        "ix_decision_records_policy_created", "decision_records", ["policy_version", "created_at"]
    )
    op.create_index("ix_decision_records_outcome_created", "decision_records", ["outcome", "created_at"])
    op.create_index("ix_decision_records_created_at", "decision_records", ["created_at"])

    op.create_table(
        "approval_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("approval_id", sa.String(32), nullable=False, unique=True),
        sa.Column(
            "decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("decision_records.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("risk_tier", sa.String(16), nullable=False),
        sa.Column("assigned_role", sa.String(64)),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_approval_requests_pending_queue",
        "approval_requests",
        ["status", "created_at"],
        postgresql_where=sa.text("status = 'PENDING'"),
    )

    op.create_table(
        "approval_resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "approval_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("approval_requests.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("approver_id", sa.String(128), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "session_context",
        sa.Column("session_id", sa.String(128), primary_key=True),
        sa.Column("rejection_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "state",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key_id", sa.String(32), nullable=False, unique=True),
        sa.Column("key_hash", sa.String(128), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("scopes", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "system_config",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("system_config")
    op.drop_table("api_keys")
    op.drop_table("session_context")
    op.drop_table("approval_resolutions")
    op.drop_index("ix_approval_requests_pending_queue", table_name="approval_requests")
    op.drop_table("approval_requests")
    op.drop_index("ix_decision_records_created_at", table_name="decision_records")
    op.drop_index("ix_decision_records_outcome_created", table_name="decision_records")
    op.drop_index("ix_decision_records_policy_created", table_name="decision_records")
    op.drop_index("ix_decision_records_agent_created", table_name="decision_records")
    op.drop_index("ix_decision_records_session_created", table_name="decision_records")
    op.drop_table("decision_records")
    op.drop_index("uq_policy_versions_single_active", table_name="policy_versions")
    op.drop_table("policy_versions")
