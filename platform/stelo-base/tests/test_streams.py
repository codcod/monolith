import asyncio
from typing import Self

import orjson
import pytest

from stelo.base.streams import consume, publish


class FakePublisher:
    def __init__(self, sent: list[bytes], fail: type[BaseException] | None) -> None:
        self.sent = sent
        self.fail = fail
        self.closed = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> bool:
        self.closed = True
        return False

    async def send(self, message: bytes) -> None:
        if self.fail:
            raise self.fail
        self.sent.append(message)


class FakeClient:
    """
    Stands in for `rbfly.streams.StreamsClient` so the wrapper's create/
    publish/consume sequencing can be tested without a real broker.
    """

    def __init__(self, messages: list[bytes] = ()) -> None:
        self.created_streams: list[str] = []
        self.sent: list[bytes] = []
        self.publishers: list[FakePublisher] = []
        self.fail_next_send: type[BaseException] | None = None
        self._messages = list(messages)

    async def create_stream(self, stream: str) -> None:
        self.created_streams.append(stream)

    def publisher(self, stream: str) -> FakePublisher:
        self.publishers.append(FakePublisher(self.sent, fail=self.fail_next_send))
        return self.publishers[-1]

    async def subscribe(self, stream: str, offset=None):
        for message in self._messages:
            yield message


async def test_publish_creates_stream_and_sends_json():
    client = FakeClient()

    await publish(client, "traffic-in", {"id": "1"})

    assert client.created_streams == ["traffic-in"]
    assert client.sent == [orjson.dumps({"id": "1"})]


async def test_consume_creates_stream_and_decodes_json():
    client = FakeClient(messages=[orjson.dumps({"id": "1"}), orjson.dumps({"id": "2"})])

    received = [message async for message in consume(client, "dispatch-in")]

    assert client.created_streams == ["dispatch-in"]
    assert received == [{"id": "1"}, {"id": "2"}]


@pytest.mark.parametrize("error", [TimeoutError, asyncio.CancelledError])
async def test_publish_drops_and_closes_a_publisher_whose_send_failed(error):
    client = FakeClient()
    client.fail_next_send = error

    with pytest.raises(error):
        await publish(client, "traffic-in", {"id": "1"})
    client.fail_next_send = None
    await publish(client, "traffic-in", {"id": "2"})
    await asyncio.sleep(0)  # let the background close run

    first, second = client.publishers
    assert first.closed
    assert not second.closed
    assert client.sent == [orjson.dumps({"id": "2"})]
