import typing as tp
from typing import Self

from monobase.uow import SqlAlchemyUnitOfWork

from stelo.inbox.adapters.repository import SqlAlchemyMessageRepository


class InboxUnitOfWork(SqlAlchemyUnitOfWork):
    messages: SqlAlchemyMessageRepository

    @tp.override
    async def __aenter__(self) -> Self:
        _ = await super().__aenter__()
        self.messages = SqlAlchemyMessageRepository(self.connection)
        return self
