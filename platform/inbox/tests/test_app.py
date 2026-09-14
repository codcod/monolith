from typing import Self

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from stelo.base.security import auth_middleware, request_id_middleware
from stelo.base.webapp import DB_KEY, RABBIT_KEY
from stelo.inbox import app as inbox_app


class FakeConnection:
    def __init__(self) -> None:
        self.inserted: list = []

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> bool:
        return False

    async def execute(self, stmt) -> None:
        self.inserted.append(stmt)


class FakeEngine:
    def __init__(self) -> None:
        self.connection = FakeConnection()

    def begin(self) -> FakeConnection:
        return self.connection


def _make_client(monkeypatch):
    published: list = []

    async def fake_publish(client, stream, message):
        published.append((stream, message))

    monkeypatch.setattr(inbox_app, 'publish', fake_publish)

    app = web.Application(
        middlewares=[request_id_middleware, auth_middleware('secret')]
    )
    app.add_routes(inbox_app.routes)
    engine = FakeEngine()
    app[DB_KEY] = engine
    app[RABBIT_KEY] = object()
    return TestClient(TestServer(app)), published, engine


async def test_health_ok(monkeypatch):
    client, _, _ = _make_client(monkeypatch)
    async with client:
        resp = await client.get('/health')
        assert resp.status == 200


async def test_create_message_requires_auth(monkeypatch):
    client, _, _ = _make_client(monkeypatch)
    async with client:
        resp = await client.post(
            '/messages',
            json={'channel': 'sms', 'recipient': '+1', 'body': 'hi'},
        )
        assert resp.status == 401


async def test_create_message_validates_payload(monkeypatch):
    client, _, _ = _make_client(monkeypatch)
    async with client:
        resp = await client.post(
            '/messages',
            json={'channel': 'carrier-pigeon', 'recipient': '+1', 'body': 'hi'},
            headers={'Authorization': 'Bearer secret'},
        )
        assert resp.status == 400


async def test_create_message_inserts_row_and_publishes(monkeypatch):
    client, published, engine = _make_client(monkeypatch)
    async with client:
        resp = await client.post(
            '/messages',
            json={'channel': 'sms', 'recipient': '+1', 'body': 'hi'},
            headers={'Authorization': 'Bearer secret'},
        )
        assert resp.status == 202
        body = await resp.json()
        assert 'id' in body

    assert len(engine.connection.inserted) == 1
    assert len(published) == 1
    stream, message = published[0]
    assert stream == 'traffic-in'
    assert message['channel'] == 'sms'
    assert message['id'] == body['id']
