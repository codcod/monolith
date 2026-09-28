from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from stelo.base.security import auth_middleware, request_id_middleware
from stelo.base.webapp import DB_KEY

from stelo.inbox.entrypoints import app as inbox_app


class FakeTransaction:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass


class FakeConnection:
    def __init__(self) -> None:
        self.inserted: list = []
        self.transaction = FakeTransaction()

    async def begin(self) -> FakeTransaction:
        return self.transaction

    async def execute(self, stmt, *args) -> None:
        self.inserted.append(stmt)

    async def close(self) -> None:
        pass


class FakeEngine:
    def __init__(self) -> None:
        self.connection = FakeConnection()

    async def connect(self) -> FakeConnection:
        return self.connection


def _make_client():
    app = web.Application(
        middlewares=[request_id_middleware, auth_middleware("secret")]
    )
    app.add_routes(inbox_app.routes)
    engine = FakeEngine()
    app[DB_KEY] = engine
    return TestClient(TestServer(app)), engine


async def test_health_ok():
    client, _ = _make_client()
    async with client:
        resp = await client.get("/health")
        assert resp.status == 200


async def test_create_message_requires_auth():
    client, _ = _make_client()
    async with client:
        resp = await client.post(
            "/messages",
            json={"channel": "sms", "recipient": "+1", "body": "hi"},
        )
        assert resp.status == 401


async def test_create_message_validates_payload():
    client, _ = _make_client()
    async with client:
        resp = await client.post(
            "/messages",
            json={"channel": "carrier-pigeon", "recipient": "+1", "body": "hi"},
            headers={"Authorization": "Bearer secret"},
        )
        assert resp.status == 400


async def test_create_message_inserts_row_and_outbox_row():
    client, engine = _make_client()
    async with client:
        resp = await client.post(
            "/messages",
            json={"channel": "sms", "recipient": "+1", "body": "hi"},
            headers={"Authorization": "Bearer secret"},
        )
        assert resp.status == 202
        body = await resp.json()
        assert "id" in body

    # the message row and its outbox row, in one committed transaction;
    # nothing is published inline any more (the relay does that)
    assert len(engine.connection.inserted) == 2
    assert engine.connection.transaction.committed
