from datetime import UTC, datetime
from types import SimpleNamespace

from stelo.admin import metrics


class FakeResult:
    """Stands in for a SQLAlchemy `Result` — only the bits metrics.py uses."""

    def __init__(self, *, scalar=None, one=None, rows=None):
        self._scalar = scalar
        self._one = one
        self._rows = rows or []

    def scalar(self):
        return self._scalar

    def one(self):
        return self._one

    def __iter__(self):
        return iter(self._rows)


class FakeConnection:
    """
    Stands in for `AsyncConnection`: `scalar()` and `execute()` each pop the
    next canned value/result off their own queue, in call order — same
    hand-rolled-fake convention as `FakeClient` in stelo-base's
    test_streams.py, not a mocking framework.
    """

    def __init__(self, *, scalars=None, results=None):
        self._scalars = list(scalars or [])
        self._results = list(results or [])

    async def scalar(self, stmt):
        return self._scalars.pop(0)

    async def execute(self, stmt, params=None):
        return self._results.pop(0)


async def test_stage_totals_counts_each_schema():
    conn = FakeConnection(scalars=[184213, 181840, 179026])
    assert await metrics.stage_totals(conn) == {
        'received': 184213,
        'routed': 181840,
        'sent': 179026,
    }


async def test_stage_totals_treats_null_count_as_zero():
    conn = FakeConnection(scalars=[None, None, None])
    assert await metrics.stage_totals(conn) == {'received': 0, 'routed': 0, 'sent': 0}


async def test_oldest_unprocessed_age_seconds():
    conn = FakeConnection(results=[FakeResult(scalar=42.5)])
    assert await metrics.oldest_unprocessed_age_seconds(conn) == 42.5


async def test_oldest_unprocessed_age_seconds_none_when_no_backlog():
    conn = FakeConnection(results=[FakeResult(scalar=None)])
    assert await metrics.oldest_unprocessed_age_seconds(conn) is None


async def test_latency_percentiles_ms():
    conn = FakeConnection(results=[FakeResult(one=(120.0, 480.0))])
    assert await metrics.latency_percentiles_ms(conn) == {'p50': 120.0, 'p95': 480.0}


async def test_error_rate_defaults_to_zero_when_no_messages():
    conn = FakeConnection(results=[FakeResult(scalar=None)])
    assert await metrics.error_rate(conn) == 0.0


async def test_channel_breakdown_maps_rows():
    row = SimpleNamespace(channel='sms', sent=82340, failed=214)
    conn = FakeConnection(results=[FakeResult(rows=[row])])
    assert await metrics.channel_breakdown(conn) == [
        {'channel': 'sms', 'sent': 82340, 'failed': 214}
    ]


async def test_recent_events_maps_rows_and_formats_timestamp():
    row = SimpleNamespace(
        id='abc',
        stage='sent',
        channel='email',
        at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    conn = FakeConnection(results=[FakeResult(rows=[row])])
    events = await metrics.recent_events(conn, limit=5)
    assert events == [
        {
            'id': 'abc',
            'stage': 'sent',
            'channel': 'email',
            'at': '2026-01-01T12:00:00+00:00',
        }
    ]
