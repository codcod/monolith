from logging.config import fileConfig

import sqlalchemy as sa
from alembic import context
from monobase.config import read_config
from monobase.migrations import run_migrations_online
from monobase.outbox import outbox_table
from sqlalchemy.dialects.postgresql import UUID

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = sa.MetaData(schema="inbox")

_ = sa.Table(
    "messages",
    target_metadata,
    sa.Column("id", UUID(), primary_key=True),
    sa.Column("channel", sa.Text(), nullable=False),
    sa.Column("recipient", sa.Text(), nullable=False),
    sa.Column("body", sa.Text(), nullable=False),
    sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
)
_ = outbox_table(target_metadata, "inbox")


def get_dsn() -> str:
    """
    The DSN comes from the module's own config.toml (same file the app
    reads), not from alembic.ini — one source of truth for the DB
    connection. Pass `-x config=<path>` to point at a different file, e.g.
    a test config.
    """
    args = context.get_x_argument(as_dictionary=True)
    config_path = args.get("config", "./config/config.toml")
    return read_config(config_path)["inbox"]["db"]


if context.is_offline_mode():
    context.configure(
        url=get_dsn(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=target_metadata.schema,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online(target_metadata, get_dsn())
