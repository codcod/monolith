import logging
from datetime import UTC, datetime

from stelo.base.channels import Sender
from stelo.base.messages import Message as WireMessage

from stelo.dispatcher.domain.model import Message
from stelo.dispatcher.service_layer.unit_of_work import DispatcherUnitOfWork

logger = logging.getLogger(__name__)


async def dispatch_message(
    incoming: WireMessage,
    uow: DispatcherUnitOfWork,
    sender: Sender,
) -> None:
    """
    Send `incoming` over its channel (stub sender only) and record the
    outcome. An id already recorded is a redelivery (traffic's outbox relay
    is at-least-once) and is skipped without sending.
    """
    async with uow:
        # ponytail: get-then-insert, safe with one consumer per stream; ON
        # CONFLICT DO NOTHING if a stream ever gets two
        if await uow.messages.get(incoming["id"]) is not None:
            logger.info("Message %s already recorded, skipping", incoming["id"])
            return
        await sender.send(incoming["recipient"], incoming["body"])
        message = Message(
            id=incoming["id"],
            channel=incoming["channel"],
            recipient=incoming["recipient"],
            send_status="sent",
            sent_at=datetime.now(UTC),
        )
        await uow.messages.add(message)
        await uow.commit()
