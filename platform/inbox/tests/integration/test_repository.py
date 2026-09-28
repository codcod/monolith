"""
Repository/UoW against a real Postgres — the one tier that needs `just up`
(or `docker compose up postgres`) first, so it's skipped by default and
kept out of the fast default `test` recipe. Run explicitly via
`RUN_INTEGRATION_TESTS=1 pytest tests/integration`.

The table is created directly here (mirroring
`migrations/versions/*_create_inbox_schema.py`) rather than by shelling out
to Alembic, to keep the fixture self-contained — this schema is the one
Alembic already owns for real, `just migrate` remains the source of truth
for what actually ships.
"""

import os
import uuid
from datetime import UTC, datetime

import pytest
import sqlalchemy as sa
from monobase.db import make_engine
from sqlalchemy.ext.asyncio import AsyncEngine

from stelo.inbox.domain.model import Message
from stelo.inbox.service_layer.unit_of_work import InboxUnitOfWork

pytestmark = pytest.mark.skipif(
    not os.environ.get("RUN_INTEGRATION_TESTS"),
    reason="needs a live Postgres — set RUN_INTEGRATION_TESTS=1 (see `just up`)",
)

TEST_DSN = os.environ.get(
    "INBOX_TEST_DB", "postgresql+asyncpg://stelo:stelo@localhost/stelo"
)


@pytest.fixture
async def engine() -> AsyncEngine:
    engine = make_engine(TEST_DSN)
    async with engine.begin() as conn:
        await conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS inbox"))
        await conn.execute(
            sa.text(
                """
                CREATE TABLE IF NOT EXISTS inbox.messages (
                    id uuid PRIMARY KEY,
                    channel text NOT NULL,
                    recipient text NOT NULL,
                    body text NOT NULL,
                    received_at timestamptz NOT NULL
                )
                """
            )
        )
    yield engine
    async with engine.begin() as conn:
        await conn.execute(sa.text("DELETE FROM inbox.messages"))
    await engine.dispose()


def _a_message() -> Message:
    return Message(
        id=str(uuid.uuid4()),
        channel="sms",
        recipient="+1",
        body="hi",
        received_at=datetime.now(UTC),
    )


async def test_add_then_get_round_trips_through_postgres(engine: AsyncEngine):
    message = _a_message()

    async with InboxUnitOfWork(engine) as uow:
        await uow.messages.add(message)
        await uow.commit()

    async with InboxUnitOfWork(engine) as uow:
        fetched = await uow.messages.get(message.id)

    assert fetched == message


async def test_exception_before_commit_leaves_no_row(engine: AsyncEngine):
    message = _a_message()

    with pytest.raises(ValueError):
        async with InboxUnitOfWork(engine) as uow:
            await uow.messages.add(message)
            raise ValueError("boom")

    async with InboxUnitOfWork(engine) as uow:
        fetched = await uow.messages.get(message.id)

    assert fetched is None
