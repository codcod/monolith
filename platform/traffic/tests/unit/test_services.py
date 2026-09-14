from stelo.base.unit_of_work import AbstractUnitOfWork
from stelo.traffic.domain.model import Message
from stelo.traffic.service_layer import services

INCOMING = {
    'id': '1',
    'channel': 'sms',
    'recipient': '+1',
    'body': 'hi',
    'status': 'received',
    'created_at': '2026-01-01T00:00:00Z',
}


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


async def test_route_message_adds_a_routing_row_and_commits():
    uow = FakeUnitOfWork()

    await services.route_message(INCOMING, uow, publish=_noop_publish)

    assert uow.committed
    assert len(uow.messages.added) == 1
    routed = uow.messages.added[0]
    assert routed.id == '1'
    assert routed.channel == 'sms'
    assert routed.recipient == '+1'


async def test_route_message_republishes_with_status_routed():
    published = []

    async def publish(message):
        published.append(message)

    await services.route_message(INCOMING, FakeUnitOfWork(), publish)

    assert published == [{**INCOMING, 'status': 'routed'}]


async def _noop_publish(message) -> None:
    pass
