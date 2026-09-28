from monobase.uow import AbstractUnitOfWork

from stelo.dispatcher.domain.model import Message
from stelo.dispatcher.service_layer import services

INCOMING = {
    "id": "1",
    "channel": "sms",
    "recipient": "+1",
    "body": "hi",
    "status": "routed",
    "created_at": "2026-01-01T00:00:00Z",
}


class FakeSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send(self, recipient: str, body: str) -> None:
        self.sent.append((recipient, body))


class FakeMessageRepository:
    def __init__(self) -> None:
        self.added: list[Message] = []

    async def add(self, item: Message) -> None:
        self.added.append(item)

    async def get(self, id: str) -> Message | None:
        return next((m for m in self.added if m.id == id), None)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.messages = FakeMessageRepository()
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass


async def test_dispatch_message_sends_via_the_given_sender():
    sender = FakeSender()

    await services.dispatch_message(INCOMING, FakeUnitOfWork(), sender)

    assert sender.sent == [("+1", "hi")]


async def test_dispatch_message_records_the_outcome_and_commits():
    uow = FakeUnitOfWork()

    await services.dispatch_message(INCOMING, uow, FakeSender())

    assert uow.committed
    assert len(uow.messages.added) == 1
    recorded = uow.messages.added[0]
    assert recorded.id == "1"
    assert recorded.send_status == "sent"


async def test_dispatch_message_skips_a_duplicate_id():
    uow = FakeUnitOfWork()
    await services.dispatch_message(INCOMING, uow, FakeSender())
    sender = FakeSender()

    await services.dispatch_message(INCOMING, uow, sender)

    assert sender.sent == []
    assert len(uow.messages.added) == 1
