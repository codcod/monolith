from datetime import UTC, datetime

from stelo.base.channels import Sender
from stelo.base.messages import Message as WireMessage
from stelo.dispatcher.domain.model import Message
from stelo.dispatcher.service_layer.unit_of_work import DispatcherUnitOfWork


async def dispatch_message(
    incoming: WireMessage,
    uow: DispatcherUnitOfWork,
    sender: Sender,
) -> None:
    """
    Send `incoming` over its channel (stub sender only) and record the
    outcome.
    """
    await sender.send(incoming['recipient'], incoming['body'])

    message = Message(
        id=incoming['id'],
        channel=incoming['channel'],
        recipient=incoming['recipient'],
        send_status='sent',
        sent_at=datetime.now(UTC),
    )

    async with uow:
        await uow.messages.add(message)
        await uow.commit()
