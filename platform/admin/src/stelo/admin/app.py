import asyncio
import contextlib
from pathlib import Path

from aiohttp import web
from stelo.base.config import Config
from stelo.base.webapp import DB_KEY, make_app

from . import metrics, render
from .datastar import patch_elements, patch_signals

routes = web.RouteTableDef()
STATIC_DIR = Path('static')
STAGES = ('received', 'routed', 'sent')
HISTORY_LEN = 30
TICK_SECONDS = 2


@routes.get('/health')
async def health(request: web.Request) -> web.Response:
    return web.json_response({'status': 'ok'})


@routes.get('/')
async def index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(STATIC_DIR / 'index.html')


@routes.get('/events')
async def events(request: web.Request) -> web.StreamResponse:
    """
    Datastar SSE feed: every tick, query current pipeline state and push one
    patch-signals event (stat numbers) plus a patch-elements event per piece
    of markup that isn't just a number (sparklines, throughput chart, channel
    bars, event feed). History for rates/sparklines lives for the lifetime of
    this one connection only.
    `# ponytail: per-connection in-memory history, each open tab re-queries
    independently — move to a shared broadcaster + DB-backed history if this
    ever needs many concurrent viewers or a longer look-back.`
    """
    response = web.StreamResponse(
        headers={'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache'}
    )
    await response.prepare(request)

    history: dict[str, list[float]] = {stage: [] for stage in STAGES}
    previous: metrics.StageTotals | None = None
    engine = request.app[DB_KEY]

    with contextlib.suppress(ConnectionResetError, asyncio.CancelledError):
        while True:
            async with engine.connect() as conn:
                totals = await metrics.stage_totals(conn)
                oldest = await metrics.oldest_unprocessed_age_seconds(conn)
                latency = await metrics.latency_percentiles_ms(conn)
                err_rate = await metrics.error_rate(conn)
                channels = await metrics.channel_breakdown(conn)
                feed = await metrics.recent_events(conn)

            rates: dict[str, float] = {}
            for stage in STAGES:
                total = totals[stage]
                prev = previous[stage] if previous else total
                rate = max(0.0, (total - prev) / TICK_SECONDS)
                rates[stage] = rate
                buf = history[stage]
                buf.append(rate)
                del buf[:-HISTORY_LEN]
            previous = totals

            signals = {
                'receivedTotal': totals['received'],
                'routedTotal': totals['routed'],
                'sentTotal': totals['sent'],
                'receivedRate': round(rates['received'], 1),
                'routedRate': round(rates['routed'], 1),
                'sentRate': round(rates['sent'], 1),
                'backlog': max(0, totals['received'] - totals['routed']),
                'latencyP50': round(latency['p50'])
                if latency['p50'] is not None
                else None,
                'latencyP95': round(latency['p95'])
                if latency['p95'] is not None
                else None,
                'errorRate': round(err_rate * 100, 2),
                'oldestUnprocessed': round(oldest) if oldest is not None else 0,
            }
            await response.write(patch_signals(signals).encode())

            for stage in STAGES:
                fragment = render.spark(
                    history[stage], render.STAGE_COLORS[stage], f'spark-{stage}'
                )
                await response.write(patch_elements(fragment).encode())
            await response.write(patch_elements(render.chart(history)).encode())
            await response.write(patch_elements(render.channel_bars(channels)).encode())
            await response.write(patch_elements(render.feed_rows(feed)).encode())

            await asyncio.sleep(TICK_SECONDS)

    return response


def build_app(config: Config) -> web.Application:
    # Admin has no mutating routes to protect — everything it serves is a
    # read-only view over the other services' data, so it skips the bearer-
    # token stub entirely rather than bolting it onto routes a browser can't
    # attach a header to anyway (see stelo.base.webapp.make_app).
    app = make_app(config, routes=routes, db_dsn=config['db'], require_auth=False)
    app.router.add_static('/static', STATIC_DIR)
    return app
