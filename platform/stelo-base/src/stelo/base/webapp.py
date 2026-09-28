import asyncio
import contextlib
import json
import typing as tp
from collections.abc import AsyncIterator, Coroutine, Iterable

from aiohttp import web
from aiohttp.typedefs import Middleware
from monobase.db import make_engine
from monobase.outbox import run_relay
from rbfly.streams import StreamsClient
from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncEngine

from .config import Config
from .security import auth_middleware, request_id_middleware
from .streams import connect, publish

CONFIG_KEY = web.AppKey("config", Config)
DB_KEY = web.AppKey("db", AsyncEngine)
RABBIT_KEY = web.AppKey("rabbit", StreamsClient)


def make_app(
    config: Config,
    *,
    routes: Iterable[web.AbstractRouteDef] = (),
    db_dsn: str | None = None,
    require_auth: bool = True,
) -> web.Application:
    """
    Build an aiohttp Application wired the same way in every module: shared
    middleware, and (if given) a RabbitMQ Streams client at app[RABBIT_KEY]
    and/or a SQLAlchemy async engine at app[DB_KEY] — both connected on
    startup and disposed on cleanup.

    `require_auth=False` drops the bearer-token middleware entirely, for a
    module with no mutating routes to protect (e.g. admin's read-only
    dashboard) — a browser navigating to a page or issuing a plain <script
    src> can't carry a custom header, so bolting the token stub onto a
    module that's public by design just breaks silently instead of
    protecting anything.
    """
    middlewares: list[Middleware] = [request_id_middleware]
    if require_auth:
        middlewares.append(auth_middleware(config.get("auth_token", "dev-token")))
    app = web.Application(middlewares=middlewares)
    app[CONFIG_KEY] = config
    _ = app.add_routes(routes)

    rabbitmq_url = config.get("rabbitmq_url")
    if rabbitmq_url:

        async def rabbit_ctx(app: web.Application) -> AsyncIterator[None]:
            client = connect(rabbitmq_url)
            app[RABBIT_KEY] = client
            yield
            await client.disconnect()

        app.cleanup_ctx.append(rabbit_ctx)

    if db_dsn:
        engine = make_engine(db_dsn)
        app[DB_KEY] = engine

        async def db_ctx(_app: web.Application) -> AsyncIterator[None]:
            yield
            await engine.dispose()

        app.cleanup_ctx.append(db_ctx)

    return app


def run_in_background(
    app: web.Application,
    factory: tp.Callable[[web.Application], Coroutine[tp.Any, tp.Any, None]],
) -> None:
    """
    Run `factory(app)` as a background task for the app's lifetime —
    started once the app (and its rabbit/db context) is up, cancelled on
    cleanup. Used by traffic/dispatcher to run their stream-consumer loop
    alongside the (health-only) HTTP surface.
    """

    async def _ctx(app: web.Application) -> AsyncIterator[None]:
        task = asyncio.create_task(factory(app))
        yield
        _ = task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    app.cleanup_ctx.append(_ctx)


def run_outbox_relay(app: web.Application, table: Table) -> None:
    """
    Run monobase's outbox relay over `table` for the app's lifetime,
    publishing each row's JSON `payload` to the stream named in its
    `destination`. Delivery is at-least-once, so consumers must tolerate a
    duplicate message id. Run one per outbox table.
    """

    async def relay(app: web.Application) -> None:
        async def deliver(row: dict[str, tp.Any]) -> None:
            payload = json.loads(row["payload"])
            await publish(app[RABBIT_KEY], row["destination"], payload)

        await run_relay(app[DB_KEY], table, deliver)

    run_in_background(app, relay)
