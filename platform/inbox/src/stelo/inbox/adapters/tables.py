import sqlalchemy as sa
from monobase.outbox import outbox_table
from sqlalchemy.dialects.postgresql import UUID

messages_table = sa.table(
    "messages",
    # typed: an untyped column binds the id as VARCHAR, and Postgres has no
    # uuid = varchar operator
    sa.column("id", UUID(as_uuid=False)),
    sa.column("channel"),
    sa.column("recipient"),
    sa.column("body"),
    sa.column("received_at"),
    schema="inbox",
)

outbox = outbox_table(sa.MetaData(), "inbox")
