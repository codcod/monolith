"""create inbox outbox

Revision ID: 4146e0755d7f
Revises: 63e29b2fa4df
Create Date: 2026-09-28 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4146e0755d7f'
down_revision: str | Sequence[str] | None = '63e29b2fa4df'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Column for column monobase.outbox.outbox_table, which the relay reads.
    _ = op.create_table(
        'outbox',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('destination', sa.String(), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='inbox',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('outbox', schema='inbox')
