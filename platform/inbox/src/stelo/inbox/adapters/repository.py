import typing as tp
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncConnection
from stelo.base.repository import AbstractRepository

from stelo.inbox.adapters.tables import messages_table
from stelo.inbox.domain.model import Channel, Message


class SqlAlchemyMessageRepository(AbstractRepository[Message]):
    connection: AsyncConnection

    def __init__(self, connection: AsyncConnection) -> None:
        self.connection = connection

    @tp.override
    async def add(self, item: Message) -> None:
        _ = await self.connection.execute(
            messages_table.insert().values(
                id=item.id,
                channel=item.channel,
                recipient=item.recipient,
                body=item.body,
                received_at=item.received_at,
            )
        )

    @tp.override
    async def get(self, id: str) -> Message | None:
        result = await self.connection.execute(
            messages_table.select().where(messages_table.c.id == id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        return Message(
            id=tp.cast(str, row.id),
            channel=tp.cast(Channel, row.channel),
            recipient=tp.cast(str, row.recipient),
            body=tp.cast(str, row.body),
            received_at=tp.cast(datetime, row.received_at),
        )
