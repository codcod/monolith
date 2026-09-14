from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from stelo.dispatcher.entrypoints import app as dispatcher_app


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

    async def execute(self, stmt) -> None:
        self.inserted.append(stmt)

    async def close(self) -> None:
        pass


class FakeEngine:
    def __init__(self) -> None:
        self.connection = FakeConnection()

    async def connect(self) -> FakeConnection:
        return self.connection


class FakeSender:
    def __init__(self) -> None:
        self.sent: list = []

    async def send(self, recipient: str, body: str) -> None:
        self.sent.append((recipient, body))


async def test_health_ok():
    app = web.Application()
    app.add_routes(dispatcher_app.routes)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/health')
        assert resp.status == 200


async def test_process_dispatch_in_sends_and_records(monkeypatch):
    incoming = {
        'id': '1',
        'channel': 'sms',
        'recipient': '+1',
        'body': 'hi',
        'status': 'routed',
        'created_at': '2026-01-01T00:00:00Z',
    }

    async def fake_consume(client, stream):
        assert stream == 'dispatch-in'
        yield incoming

    monkeypatch.setattr(dispatcher_app, 'consume', fake_consume)

    fake_sender = FakeSender()
    monkeypatch.setattr(dispatcher_app, 'SENDERS', {'sms': fake_sender})

    engine = FakeEngine()
    app = {dispatcher_app.DB_KEY: engine, dispatcher_app.RABBIT_KEY: object()}

    await dispatcher_app.process_dispatch_in(app)

    assert fake_sender.sent == [('+1', 'hi')]
    assert len(engine.connection.inserted) == 1
    assert engine.connection.transaction.committed
