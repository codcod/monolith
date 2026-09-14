from typing import Self

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from stelo.traffic import app as traffic_app


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


async def test_health_ok():
    app = web.Application()
    app.add_routes(traffic_app.routes)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/health')
        assert resp.status == 200


async def test_process_traffic_in_inserts_and_republishes(monkeypatch):
    incoming = {
        'id': '1',
        'channel': 'sms',
        'recipient': '+1',
        'body': 'hi',
        'status': 'received',
        'created_at': '2026-01-01T00:00:00Z',
    }

    async def fake_consume(client, stream):
        assert stream == 'traffic-in'
        yield incoming

    published: list = []

    async def fake_publish(client, stream, message):
        published.append((stream, message))

    monkeypatch.setattr(traffic_app, 'consume', fake_consume)
    monkeypatch.setattr(traffic_app, 'publish', fake_publish)

    engine = FakeEngine()
    app = {traffic_app.DB_KEY: engine, traffic_app.RABBIT_KEY: object()}

    await traffic_app.process_traffic_in(app)

    assert len(engine.connection.inserted) == 1
    assert len(published) == 1
    stream, message = published[0]
    assert stream == 'dispatch-in'
    assert message['status'] == 'routed'
    assert message['id'] == '1'
