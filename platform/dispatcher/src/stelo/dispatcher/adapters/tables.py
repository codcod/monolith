import sqlalchemy as sa

messages_table = sa.table(
    'messages',
    sa.column('id'),
    sa.column('channel'),
    sa.column('recipient'),
    sa.column('send_status'),
    sa.column('sent_at'),
    schema='dispatcher',
)
