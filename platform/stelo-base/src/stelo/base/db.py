from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def make_engine(dsn: str) -> AsyncEngine:
    """
    Build an async SQLAlchemy core engine for a module's database.

    All modules connect to the same physical database the same way; each
    module keeps its own schema and defines its own `sqlalchemy.Table`
    objects (with `schema=<module name>`) against this engine.
    """
    return create_async_engine(dsn, pool_pre_ping=True)
