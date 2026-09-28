from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from stelo.traffic.entrypoints import app as traffic_app


class FakeTransaction:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass


class FakeResult:
    def one_or_none(self) -> None:
        return None


class FakeConnection:
    def __init__(self) -> None:
        self.inserted: list = []
        self.transaction = FakeTransaction()

    async def begin(self) -> FakeTransaction:
        return self.transaction

    async def execute(self, stmt, *args) -> "FakeResult":
        self.inserted.append(stmt)
        return FakeResult()

    async def close(self) -> None:
        pass


class FakeEngine:
    def __init__(self) -> None:
        self.connection = FakeConnection()

    async def connect(self) -> FakeConnection:
        return self.connection


async def test_health_ok():
    app = web.Application()
    app.add_routes(traffic_app.routes)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get("/health")
        assert resp.status == 200


async def test_process_traffic_in_records_and_enqueues(monkeypatch):
    incoming = {
        "id": "1",
        "channel": "sms",
        "recipient": "+1",
        "body": "hi",
        "status": "received",
        "created_at": "2026-01-01T00:00:00Z",
    }

    async def fake_consume(client, stream):
        assert stream == "traffic-in"
        yield incoming

    monkeypatch.setattr(traffic_app, "consume", fake_consume)

    engine = FakeEngine()
    app = {traffic_app.DB_KEY: engine, traffic_app.RABBIT_KEY: object()}

    await traffic_app.process_traffic_in(app)

    # the duplicate check, the routing row and its outbox row, committed;
    # nothing is published inline any more (the relay does that)
    assert len(engine.connection.inserted) == 3
    assert engine.connection.transaction.committed
