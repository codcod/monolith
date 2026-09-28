import typing as tp

from monobase.outbox import OutboxRepository
from monobase.uow import SqlAlchemyUnitOfWork

from stelo.traffic.adapters import tables
from stelo.traffic.adapters.repository import SqlAlchemyMessageRepository


class TrafficUnitOfWork(SqlAlchemyUnitOfWork):
    messages: SqlAlchemyMessageRepository
    outbox: OutboxRepository

    @tp.override
    async def __aenter__(self) -> tp.Self:
        _ = await super().__aenter__()
        self.messages = SqlAlchemyMessageRepository(self.connection)
        self.outbox = OutboxRepository(self.connection, tables.outbox)
        return self
