"""Rename approval_resolutions.approval_id FK to approval_request_id for clarity."""

from typing import Sequence, Union

from alembic import op

revision: str = "002_resolution_fk_rename"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "approval_resolutions",
        "approval_id",
        new_column_name="approval_request_id",
    )


def downgrade() -> None:
    op.alter_column(
        "approval_resolutions",
        "approval_request_id",
        new_column_name="approval_id",
    )
