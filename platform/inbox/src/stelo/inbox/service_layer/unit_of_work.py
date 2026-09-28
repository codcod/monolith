import typing as tp
from typing import Self

from monobase.outbox import OutboxRepository
from monobase.uow import SqlAlchemyUnitOfWork

from stelo.inbox.adapters import tables
from stelo.inbox.adapters.repository import SqlAlchemyMessageRepository


class InboxUnitOfWork(SqlAlchemyUnitOfWork):
    messages: SqlAlchemyMessageRepository
    outbox: OutboxRepository

    @tp.override
    async def __aenter__(self) -> Self:
        _ = await super().__aenter__()
        self.messages = SqlAlchemyMessageRepository(self.connection)
        self.outbox = OutboxRepository(self.connection, tables.outbox)
        return self
