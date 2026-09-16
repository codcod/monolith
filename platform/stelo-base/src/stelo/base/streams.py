import asyncio
import typing as tp
import weakref
from collections.abc import AsyncIterator, Mapping

import orjson
from rbfly.streams import Offset, StreamsClient, streams_client

# One rbfly publisher per (client, stream), reused for the client's
# lifetime. Opening and tearing one down each cost a broker round trip and
# a slot in a fixed-size, connection-scoped slot map — opening a fresh one
# per message exhausts that slot map under concurrent load ("Slot map is
# full" / "Maximum number of publishers created").
#
# The lock below serializes every publish for a given client, not just
# publisher creation: rbfly's Publisher reads its message-id counter, awaits
# the broker round trip, then increments it — two separate awaits, not one
# atomic step — so concurrent send()s on the same publisher race and land
# on the same publishing id, which the broker then treats as a duplicate
# and never confirms, hanging the caller.
# Each entry holds (context_manager, publisher): the context manager must
# stay referenced too, or it's garbage-collected, which runs its `finally`
# and tears the publisher down server-side out from under the cached
# (now-dead) publisher object.
_publishers: 'weakref.WeakKeyDictionary[StreamsClient, dict[str, tuple[tp.Any, tp.Any]]]' = weakref.WeakKeyDictionary()
_publisher_locks: 'weakref.WeakKeyDictionary[StreamsClient, asyncio.Lock]' = (
    weakref.WeakKeyDictionary()
)


def connect(broker_url: str) -> StreamsClient:
    """
    Build a RabbitMQ Streams client. Connection itself is lazy (made on
    first `create_stream`/`publisher`/`subscribe` call); call
    `await client.disconnect()` when done with it.
    """
    return streams_client(broker_url)


async def publish(
    client: StreamsClient, stream: str, message: Mapping[str, tp.Any]
) -> None:
    """
    Publish a message (as JSON) to `stream`, creating it and its publisher
    on first use.
    """
    lock = _publisher_locks.setdefault(client, asyncio.Lock())
    async with lock:
        streams = _publishers.setdefault(client, {})
        entry = streams.get(stream)
        if entry is None:
            _ = await client.create_stream(stream)
            cm = client.publisher(stream)
            publisher = await cm.__aenter__()
            entry = (cm, publisher)
            streams[stream] = entry

        _, publisher = entry
        _ = await publisher.send(orjson.dumps(message))


async def consume(
    client: StreamsClient, stream: str
) -> AsyncIterator[dict[str, tp.Any]]:
    """
    Consume JSON messages from `stream` from the point of subscription
    onward, creating the stream first if needed.
    """
    _ = await client.create_stream(stream)
    async for body in client.subscribe(stream, offset=Offset.NEXT):
        # We only ever publish bytes (see publish() above), so the body we
        # get back is always bytes too, not the full AMQPBody union.
        yield orjson.loads(tp.cast(bytes, body))
