from sqlalchemy.ext.asyncio import AsyncConnection
from stelo.base.repository import AbstractRepository
from stelo.traffic.adapters.tables import messages_table
from stelo.traffic.domain.model import Message


class SqlAlchemyMessageRepository(AbstractRepository[Message]):
    def __init__(self, connection: AsyncConnection) -> None:
        self.connection = connection

    async def add(self, item: Message) -> None:
        await self.connection.execute(
            messages_table.insert().values(
                id=item.id,
                channel=item.channel,
                recipient=item.recipient,
                routed_at=item.routed_at,
            )
        )

    async def get(self, id: str) -> Message | None:
        result = await self.connection.execute(
            messages_table.select().where(messages_table.c.id == id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        return Message(
            id=row.id,
            channel=row.channel,
            recipient=row.recipient,
            routed_at=row.routed_at,
        )
