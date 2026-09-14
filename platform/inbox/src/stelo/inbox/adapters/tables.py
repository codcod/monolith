import sqlalchemy as sa

messages_table = sa.table(
    'messages',
    sa.column('id'),
    sa.column('channel'),
    sa.column('recipient'),
    sa.column('body'),
    sa.column('received_at'),
    schema='inbox',
)
