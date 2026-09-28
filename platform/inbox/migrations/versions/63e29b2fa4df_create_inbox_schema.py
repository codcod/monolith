"""create inbox schema

Revision ID: 63e29b2fa4df
Revises:
Create Date: 2026-09-13 12:28:12.909056

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '63e29b2fa4df'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE SCHEMA IF NOT EXISTS inbox')
    _ = op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('channel', sa.Text(), nullable=False),
        sa.Column('recipient', sa.Text(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='inbox',
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Not dropping the inbox schema itself: alembic's own version table
    # (version_table_schema="inbox", see monobase.migrations) lives in
    # it and alembic still needs it to record this downgrade.
    op.drop_table('messages', schema='inbox')
