import asyncio
import contextlib
import typing as tp
import weakref
from collections.abc import AsyncIterator, Mapping

import orjson
from rbfly.streams import Offset, StreamsClient, streams_client

# One rbfly publisher per (client, stream), reused for the client's
# lifetime unless a send on it fails (see `publish`). Opening and tearing
# one down each cost a broker round trip and a slot in a fixed-size,
# connection-scoped slot map — opening a fresh one per message exhausts that
# slot map under concurrent load ("Slot map is full" / "Maximum number of
# publishers created").
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
_publishers: "weakref.WeakKeyDictionary[StreamsClient, dict[str, tuple[tp.Any, tp.Any]]]" = weakref.WeakKeyDictionary()  # noqa: E501
_publisher_locks: "weakref.WeakKeyDictionary[StreamsClient, asyncio.Lock]" = (
    weakref.WeakKeyDictionary()
)
# Strong refs to in-flight closes of evicted publishers: the event loop holds
# tasks only weakly.
# ponytail: the close runs outside the lock above, so it relies on the broker
# answering its delete before the next publish creates a publisher (rbfly
# frees the slot id twice, and could clear a new publisher that reused it);
# await the pending close before creating a publisher if that ever bites.
_closing: set[asyncio.Task[None]] = set()


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
        try:
            _ = await publisher.send(orjson.dumps(message))
        except BaseException:
            # A send that failed or was cancelled mid-flight (e.g. by the
            # outbox relay's deliver_timeout) can leave the publisher's
            # message-id counter behind (see above), so every later send on
            # it would hang. Drop it: a fresh publisher asks the broker for
            # its last id. Close the old one too, or it stays declared on the
            # broker and the fresh one can be refused; in the background,
            # since this task may be cancelled and a close on a broken
            # connection must not hold the lock.
            cm, _ = streams.pop(stream)
            task = asyncio.ensure_future(_close_quietly(cm))
            _closing.add(task)
            task.add_done_callback(_closing.discard)
            raise


async def _close_quietly(cm: tp.Any) -> None:
    with contextlib.suppress(Exception):
        _ = await cm.__aexit__(None, None, None)


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
