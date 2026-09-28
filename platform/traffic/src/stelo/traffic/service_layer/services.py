import json
import logging
from datetime import UTC, datetime

from stelo.base.messages import Message as WireMessage

from stelo.traffic.domain.model import Message
from stelo.traffic.service_layer.uow import TrafficUnitOfWork

logger = logging.getLogger(__name__)


async def route_message(
    incoming: WireMessage,
    uow: TrafficUnitOfWork,
) -> None:
    """
    Record a routing row for `incoming` and, in the same transaction,
    enqueue it for dispatcher on the outbox, unchanged (no real routing
    logic — the channel is whatever the original request specified). An id
    already recorded is a redelivery (the relays are at-least-once) and is
    skipped.
    """
    message = Message(
        id=incoming["id"],
        channel=incoming["channel"],
        recipient=incoming["recipient"],
        routed_at=datetime.now(UTC),
    )

    outgoing: WireMessage = {**incoming, "status": "routed"}

    async with uow:
        # ponytail: get-then-insert, safe with one consumer per stream; ON
        # CONFLICT DO NOTHING if a stream ever gets two
        if await uow.messages.get(message.id) is not None:
            logger.info("Message %s already recorded, skipping", message.id)
            return
        await uow.messages.add(message)
        await uow.outbox.add(
            [
                {
                    "event_id": message.id,
                    "event_type": "MessageRouted",
                    "destination": "dispatch-in",
                    "payload": json.dumps(outgoing),
                }
            ]
        )
        await uow.commit()
