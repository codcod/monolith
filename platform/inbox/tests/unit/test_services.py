import json

from monobase.uow import AbstractUnitOfWork

from stelo.inbox.domain.model import Message
from stelo.inbox.service_layer import services


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


async def test_submit_message_adds_the_message_and_commits():
    uow = FakeUnitOfWork()

    result = await services.submit_message("sms", "+1", "hi", uow)

    assert uow.committed
    assert uow.messages.added == [result]
    assert result.channel == "sms"
    assert result.recipient == "+1"
    assert result.body == "hi"


async def test_submit_message_enqueues_the_wire_shape_before_commit():
    class TrackingUnitOfWork(FakeUnitOfWork):
        async def commit(self) -> None:
            self.rows_at_commit = list(self.outbox.rows)
            await super().commit()

    uow = TrackingUnitOfWork()
    result = await services.submit_message("email", "a@b.com", "hi", uow)

    [row] = uow.rows_at_commit
    assert row["event_id"] == result.id
    assert row["event_type"] == "MessageReceived"
    assert row["destination"] == "traffic-in"
    assert json.loads(row["payload"]) == {
        "id": result.id,
        "channel": "email",
        "recipient": "a@b.com",
        "body": "hi",
        "status": "received",
        "created_at": result.received_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
