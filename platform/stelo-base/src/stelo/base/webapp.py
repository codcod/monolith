import asyncio
import contextlib
import typing as tp

from aiohttp import web
from rbfly.streams import StreamsClient
from sqlalchemy.ext.asyncio import AsyncEngine

from .config import Config
from .db import make_engine
from .security import auth_middleware, request_id_middleware
from .streams import connect

CONFIG_KEY = web.AppKey('config', dict)
DB_KEY = web.AppKey('db', AsyncEngine)
RABBIT_KEY = web.AppKey('rabbit', StreamsClient)


def make_app(
    config: Config,
    *,
    routes: tp.Iterable[web.AbstractRouteDef] = (),
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
    middlewares = [request_id_middleware]
    if require_auth:
        middlewares.append(auth_middleware(config.get('auth_token', 'dev-token')))
    app = web.Application(middlewares=middlewares)
    app[CONFIG_KEY] = config
    app.add_routes(routes)

    if config.get('rabbitmq_url'):

        async def rabbit_ctx(app: web.Application):
            client = connect(config['rabbitmq_url'])
            app[RABBIT_KEY] = client
            yield
            await client.disconnect()

        app.cleanup_ctx.append(rabbit_ctx)

    if db_dsn:
        engine = make_engine(db_dsn)
        app[DB_KEY] = engine

        async def db_ctx(app: web.Application):
            yield
            await engine.dispose()

        app.cleanup_ctx.append(db_ctx)

    return app


def run_in_background(
    app: web.Application,
    factory: tp.Callable[[web.Application], tp.Coroutine[tp.Any, tp.Any, None]],
) -> None:
    """
    Run `factory(app)` as a background task for the app's lifetime —
    started once the app (and its rabbit/db context) is up, cancelled on
    cleanup. Used by traffic/dispatcher to run their stream-consumer loop
    alongside the (health-only) HTTP surface.
    """

    async def _ctx(app: web.Application):
        task = asyncio.create_task(factory(app))
        yield
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    app.cleanup_ctx.append(_ctx)
