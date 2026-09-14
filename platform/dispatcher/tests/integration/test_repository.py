"""
Repository/UoW against a real Postgres — skipped by default, see
`platform/inbox/tests/integration/test_repository.py` for the rationale.
Run explicitly via `RUN_INTEGRATION_TESTS=1 pytest tests/integration`.
"""

import os
import uuid
from datetime import UTC, datetime

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine
from stelo.base.db import make_engine
from stelo.dispatcher.domain.model import Message
from stelo.dispatcher.service_layer.unit_of_work import DispatcherUnitOfWork

pytestmark = pytest.mark.skipif(
    not os.environ.get('RUN_INTEGRATION_TESTS'),
    reason='needs a live Postgres — set RUN_INTEGRATION_TESTS=1 (see `just up`)',
)

TEST_DSN = os.environ.get(
    'DISPATCHER_TEST_DB', 'postgresql+asyncpg://stelo:stelo@localhost/stelo'
)


@pytest.fixture
async def engine() -> AsyncEngine:
    engine = make_engine(TEST_DSN)
    async with engine.begin() as conn:
        await conn.execute(sa.text('CREATE SCHEMA IF NOT EXISTS dispatcher'))
        await conn.execute(
            sa.text(
                """
                CREATE TABLE IF NOT EXISTS dispatcher.messages (
                    id uuid PRIMARY KEY,
                    channel text NOT NULL,
                    recipient text NOT NULL,
                    send_status text NOT NULL,
                    sent_at timestamptz NOT NULL
                )
                """
            )
        )
    yield engine
    async with engine.begin() as conn:
        await conn.execute(sa.text('DELETE FROM dispatcher.messages'))
    await engine.dispose()


def _a_message() -> Message:
    return Message(
        id=str(uuid.uuid4()),
        channel='sms',
        recipient='+1',
        send_status='sent',
        sent_at=datetime.now(UTC),
    )


async def test_add_then_get_round_trips_through_postgres(engine: AsyncEngine):
    message = _a_message()

    async with DispatcherUnitOfWork(engine) as uow:
        await uow.messages.add(message)
        await uow.commit()

    async with DispatcherUnitOfWork(engine) as uow:
        fetched = await uow.messages.get(message.id)

    assert fetched == message


async def test_exception_before_commit_leaves_no_row(engine: AsyncEngine):
    message = _a_message()

    with pytest.raises(ValueError):
        async with DispatcherUnitOfWork(engine) as uow:
            await uow.messages.add(message)
            raise ValueError('boom')

    async with DispatcherUnitOfWork(engine) as uow:
        fetched = await uow.messages.get(message.id)

    assert fetched is None
