from datetime import UTC, datetime

import sqlalchemy as sa
from aiohttp import web
from stelo.base.config import Config
from stelo.base.streams import consume, publish
from stelo.base.webapp import DB_KEY, RABBIT_KEY, make_app, run_in_background

messages_table = sa.table(
    'messages',
    sa.column('id'),
    sa.column('channel'),
    sa.column('recipient'),
    sa.column('routed_at'),
    schema='traffic',
)

routes = web.RouteTableDef()


@routes.get('/health')
async def health(request: web.Request) -> web.Response:
    return web.json_response({'status': 'ok'})


async def process_traffic_in(app: web.Application) -> None:
    """
    Consume inbox's traffic-in stream, record a routing row, and hand each
    message off to dispatcher unchanged. No real routing logic here — the
    channel is whatever the original request specified.
    """
    async for message in consume(app[RABBIT_KEY], 'traffic-in'):
        async with app[DB_KEY].begin() as conn:
            await conn.execute(
                messages_table.insert().values(
                    id=message['id'],
                    channel=message['channel'],
                    recipient=message['recipient'],
                    routed_at=datetime.now(UTC),
                )
            )

        message['status'] = 'routed'
        await publish(app[RABBIT_KEY], 'dispatch-in', message)


def build_app(config: Config) -> web.Application:
    app = make_app(config, routes=routes, db_dsn=config['db'])
    run_in_background(app, process_traffic_in)
    return app
