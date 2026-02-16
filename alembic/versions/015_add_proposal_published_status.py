"""Add enum values for ProposalStatus and WebhookDeliveryStatus.

Revision ID: 015
Revises: 014
Create Date: 2026-02-16

Adds:
- ProposalStatus.PUBLISHED: terminal state after a proposal is published
  as a contract, so it cannot be published again and resolved_at is set.
- WebhookDeliveryStatus.DEAD_LETTERED: status for events queued in the
  dead letter queue when the circuit breaker is open.

PostgreSQL only — SQLite uses VARCHAR for enums so no migration is needed.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "015"
down_revision: str = "014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _is_sqlite() -> bool:
    """Check if we're running against SQLite."""
    bind = op.get_bind()
    return bind.dialect.name == "sqlite"


def upgrade() -> None:
    """Add new enum values."""
    if _is_sqlite():
        # SQLite stores enums as VARCHAR — no schema change needed.
        return

    op.execute("ALTER TYPE proposalstatus ADD VALUE IF NOT EXISTS 'published' AFTER 'approved'")
    op.execute(
        "ALTER TYPE webhookdeliverystatus ADD VALUE IF NOT EXISTS 'dead_lettered' AFTER 'failed'"
    )


def downgrade() -> None:
    """PostgreSQL does not support removing enum values.

    The new values will remain in the types but be unused after downgrade.
    """
    pass
