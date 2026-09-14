import typing as tp

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from .tables import dispatcher_messages, inbox_messages, traffic_messages

Channel = tp.Literal['sms', 'email', 'whatsapp']


class StageTotals(tp.TypedDict):
    received: int
    routed: int
    sent: int


class ChannelCounts(tp.TypedDict):
    channel: str
    sent: int
    failed: int


class Event(tp.TypedDict):
    id: str
    stage: str
    channel: str
    at: str


async def stage_totals(conn: AsyncConnection) -> StageTotals:
    received = await conn.scalar(sa.select(sa.func.count()).select_from(inbox_messages))
    routed = await conn.scalar(sa.select(sa.func.count()).select_from(traffic_messages))
    sent = await conn.scalar(
        sa.select(sa.func.count()).select_from(dispatcher_messages)
    )
    return {
        'received': received or 0,
        'routed': routed or 0,
        'sent': sent or 0,
    }


async def oldest_unprocessed_age_seconds(conn: AsyncConnection) -> float | None:
    """
    Age of the oldest inbox row with no matching traffic row yet — how long
    the longest-stuck message has been waiting to be routed.
    """
    result = await conn.execute(
        sa.text("""
            SELECT extract(epoch from (now() - min(i.received_at)))
            FROM inbox.messages i
            LEFT JOIN traffic.messages t ON t.id = i.id
            WHERE t.id IS NULL
        """)
    )
    return result.scalar()


async def latency_percentiles_ms(conn: AsyncConnection) -> dict[str, float | None]:
    """
    p50/p95 end-to-end latency (receive -> send), in milliseconds, over the
    most recently dispatched ~500 messages.
    """
    result = await conn.execute(
        sa.text("""
            SELECT
                percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_s) * 1000,
                percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_s) * 1000
            FROM (
                SELECT extract(epoch from (d.sent_at - i.received_at)) AS latency_s
                FROM inbox.messages i
                JOIN dispatcher.messages d ON d.id = i.id
                ORDER BY i.received_at DESC
                LIMIT 500
            ) recent
        """)
    )
    p50, p95 = result.one()
    return {'p50': p50, 'p95': p95}


async def error_rate(conn: AsyncConnection) -> float:
    result = await conn.execute(
        sa.text("""
            SELECT
                count(*) FILTER (WHERE send_status != 'sent')::float
                / NULLIF(count(*), 0)
            FROM dispatcher.messages
        """)
    )
    return result.scalar() or 0.0


async def channel_breakdown(conn: AsyncConnection) -> list[ChannelCounts]:
    result = await conn.execute(
        sa.text("""
            SELECT
                channel,
                count(*) FILTER (WHERE send_status = 'sent') AS sent,
                count(*) FILTER (WHERE send_status != 'sent') AS failed
            FROM dispatcher.messages
            GROUP BY channel
            ORDER BY channel
        """)
    )
    return [
        {'channel': row.channel, 'sent': row.sent, 'failed': row.failed}
        for row in result
    ]


async def recent_events(conn: AsyncConnection, limit: int = 20) -> list[Event]:
    result = await conn.execute(
        sa.text("""
            SELECT id, 'received' AS stage, channel, received_at AS at
            FROM inbox.messages
            UNION ALL
            SELECT id, 'routed' AS stage, channel, routed_at AS at
            FROM traffic.messages
            UNION ALL
            SELECT id, CASE WHEN send_status = 'sent' THEN 'sent' ELSE 'failed' END AS stage,
                   channel, sent_at AS at
            FROM dispatcher.messages
            ORDER BY at DESC
            LIMIT :limit
        """),
        {'limit': limit},
    )
    return [
        {
            'id': str(row.id),
            'stage': row.stage,
            'channel': row.channel,
            'at': row.at.isoformat(),
        }
        for row in result
    ]
