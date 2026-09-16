import typing as tp
import uuid
from collections.abc import Awaitable
from datetime import UTC, datetime

from stelo.base.messages import Message as WireMessage

from stelo.inbox.domain.model import Channel, Message
from stelo.inbox.service_layer.unit_of_work import InboxUnitOfWork

PublishFn = tp.Callable[[WireMessage], Awaitable[None]]


async def submit_message(
    channel: Channel,
    recipient: str,
    body: str,
    uow: InboxUnitOfWork,
    publish: PublishFn,
) -> Message:
    message = Message(
        id=str(uuid.uuid4()),
        channel=channel,
        recipient=recipient,
        body=body,
        received_at=datetime.now(UTC),
    )

    async with uow:
        await uow.messages.add(message)
        await uow.commit()

    wire_message: WireMessage = {
        "id": message.id,
        "channel": message.channel,
        "recipient": message.recipient,
        "body": message.body,
        "status": "received",
        "created_at": message.received_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    await publish(wire_message)

    return message
