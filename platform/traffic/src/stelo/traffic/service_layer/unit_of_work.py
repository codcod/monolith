from typing import Self

from stelo.base.unit_of_work import SqlAlchemyUnitOfWork
from stelo.traffic.adapters.repository import SqlAlchemyMessageRepository


class TrafficUnitOfWork(SqlAlchemyUnitOfWork):
    messages: SqlAlchemyMessageRepository

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self.messages = SqlAlchemyMessageRepository(self.connection)
        return self
