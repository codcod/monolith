import sqlalchemy as sa

# Read-only refs into the other three modules' schemas — admin owns no
# schema of its own, and never writes through these. Column sets mirror
# each module's own `adapters.tables.messages_table` declaration exactly.
# There's no shared Table definition across services (admin only depends
# on stelo-base, not on inbox/traffic/dispatcher's own packages), so this
# follows the same per-module-redeclares-its-columns convention rather
# than introducing a cross-service import.

inbox_messages = sa.table(
    "messages",
    sa.column("id"),
    sa.column("channel"),
    sa.column("recipient"),
    sa.column("body"),
    sa.column("received_at"),
    schema="inbox",
)

traffic_messages = sa.table(
    "messages",
    sa.column("id"),
    sa.column("channel"),
    sa.column("recipient"),
    sa.column("routed_at"),
    schema="traffic",
)

dispatcher_messages = sa.table(
    "messages",
    sa.column("id"),
    sa.column("channel"),
    sa.column("recipient"),
    sa.column("send_status"),
    sa.column("sent_at"),
    schema="dispatcher",
)
