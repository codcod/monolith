import typing as tp
from typing import Self

from stelo.base.unit_of_work import SqlAlchemyUnitOfWork

from stelo.dispatcher.adapters.repository import SqlAlchemyMessageRepository


class DispatcherUnitOfWork(SqlAlchemyUnitOfWork):
    messages: SqlAlchemyMessageRepository

    @tp.override
    async def __aenter__(self) -> Self:
        _ = await super().__aenter__()
        self.messages = SqlAlchemyMessageRepository(self.connection)
        return self
