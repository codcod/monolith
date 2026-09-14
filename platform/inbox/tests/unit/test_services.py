from stelo.base.unit_of_work import AbstractUnitOfWork
from stelo.inbox.domain.model import Message
from stelo.inbox.service_layer import services


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


async def test_submit_message_adds_the_message_and_commits():
    uow = FakeUnitOfWork()

    result = await services.submit_message(
        'sms', '+1', 'hi', uow, publish=_noop_publish
    )

    assert uow.committed
    assert uow.messages.added == [result]
    assert result.channel == 'sms'
    assert result.recipient == '+1'
    assert result.body == 'hi'


async def test_submit_message_publishes_the_wire_shape_after_commit():
    published = []

    async def publish(message):
        published.append(message)

    result = await services.submit_message(
        'email', 'a@b.com', 'hi', FakeUnitOfWork(), publish
    )

    assert published == [
        {
            'id': result.id,
            'channel': 'email',
            'recipient': 'a@b.com',
            'body': 'hi',
            'status': 'received',
            'created_at': result.received_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
    ]


async def test_submit_message_publishes_only_after_commit():
    order: list[str] = []

    class TrackingUnitOfWork(FakeUnitOfWork):
        async def commit(self) -> None:
            order.append('commit')
            await super().commit()

    async def publish(message):
        order.append('publish')

    await services.submit_message('sms', '+1', 'hi', TrackingUnitOfWork(), publish)

    assert order == ['commit', 'publish']


async def _noop_publish(message) -> None:
    pass
