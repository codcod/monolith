from sqlalchemy.ext.asyncio import AsyncEngine

from stelo.base.db import make_engine


def test_make_engine_returns_async_engine_without_connecting():
    engine = make_engine('postgresql+asyncpg://stelo:stelo@localhost/stelo')

    assert isinstance(engine, AsyncEngine)
