import typing as tp
from collections.abc import Awaitable
from datetime import UTC, datetime

from stelo.base.messages import Message as WireMessage

from stelo.traffic.domain.model import Message
from stelo.traffic.service_layer.unit_of_work import TrafficUnitOfWork

PublishFn = tp.Callable[[WireMessage], Awaitable[None]]


async def route_message(
    incoming: WireMessage,
    uow: TrafficUnitOfWork,
    publish: PublishFn,
) -> None:
    """
    Record a routing row for `incoming`, then hand it off to dispatcher
    unchanged (no real routing logic — the channel is whatever the original
    request specified).
    """
    message = Message(
        id=incoming["id"],
        channel=incoming["channel"],
        recipient=incoming["recipient"],
        routed_at=datetime.now(UTC),
    )

    async with uow:
        await uow.messages.add(message)
        await uow.commit()

    outgoing: WireMessage = {**incoming, "status": "routed"}
    await publish(outgoing)
