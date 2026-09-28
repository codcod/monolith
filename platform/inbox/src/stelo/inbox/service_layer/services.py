import json
import uuid
from datetime import UTC, datetime

from stelo.base.messages import Message as WireMessage

from stelo.inbox.domain.model import Channel, Message
from stelo.inbox.service_layer.unit_of_work import InboxUnitOfWork


async def submit_message(
    channel: Channel,
    recipient: str,
    body: str,
    uow: InboxUnitOfWork,
) -> Message:
    """
    Store the message and, in the same transaction, enqueue its wire shape
    for `traffic-in` on the outbox; the relay publishes it after commit.
    """
    message = Message(
        id=str(uuid.uuid4()),
        channel=channel,
        recipient=recipient,
        body=body,
        received_at=datetime.now(UTC),
    )

    wire_message: WireMessage = {
        "id": message.id,
        "channel": message.channel,
        "recipient": message.recipient,
        "body": message.body,
        "status": "received",
        "created_at": message.received_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    async with uow:
        await uow.messages.add(message)
        await uow.outbox.add(
            [
                {
                    "event_id": message.id,
                    "event_type": "MessageReceived",
                    "destination": "traffic-in",
                    "payload": json.dumps(wire_message),
                }
            ]
        )
        await uow.commit()

    return message
