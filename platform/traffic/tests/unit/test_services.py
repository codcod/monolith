import json

from monobase.uow import AbstractUnitOfWork

from stelo.traffic.domain.model import Message
from stelo.traffic.service_layer import services

INCOMING = {
    "id": "1",
    "channel": "sms",
    "recipient": "+1",
    "body": "hi",
    "status": "received",
    "created_at": "2026-01-01T00:00:00Z",
}


class FakeMessageRepository:
    def __init__(self) -> None:
        self.added: list[Message] = []

    async def add(self, item: Message) -> None:
        self.added.append(item)

    async def get(self, id: str) -> Message | None:
        return next((m for m in self.added if m.id == id), None)


class FakeOutbox:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    async def add(self, rows: list[dict]) -> None:
        self.rows.extend(rows)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.messages = FakeMessageRepository()
        self.outbox = FakeOutbox()
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass


async def test_route_message_adds_a_routing_row_and_commits():
    uow = FakeUnitOfWork()

    await services.route_message(INCOMING, uow)

    assert uow.committed
    assert len(uow.messages.added) == 1
    routed = uow.messages.added[0]
    assert routed.id == "1"
    assert routed.channel == "sms"
    assert routed.recipient == "+1"


async def test_route_message_enqueues_it_for_dispatch_before_commit():
    class TrackingUnitOfWork(FakeUnitOfWork):
        async def commit(self) -> None:
            self.rows_at_commit = list(self.outbox.rows)
            await super().commit()

    uow = TrackingUnitOfWork()
    await services.route_message(INCOMING, uow)

    [row] = uow.rows_at_commit
    assert row["event_id"] == "1"
    assert row["event_type"] == "MessageRouted"
    assert row["destination"] == "dispatch-in"
    assert json.loads(row["payload"]) == {**INCOMING, "status": "routed"}


async def test_route_message_skips_a_duplicate_id():
    uow = FakeUnitOfWork()
    await services.route_message(INCOMING, uow)
    uow.committed = False

    await services.route_message(INCOMING, uow)

    assert len(uow.messages.added) == 1
    assert len(uow.outbox.rows) == 1
    assert not uow.committed
