from datetime import UTC, datetime

import sqlalchemy as sa
from aiohttp import web
from stelo.base.channels import SENDERS
from stelo.base.config import Config
from stelo.base.streams import consume
from stelo.base.webapp import DB_KEY, RABBIT_KEY, make_app, run_in_background

messages_table = sa.table(
    'messages',
    sa.column('id'),
    sa.column('channel'),
    sa.column('recipient'),
    sa.column('send_status'),
    sa.column('sent_at'),
    schema='dispatcher',
)

routes = web.RouteTableDef()


@routes.get('/health')
async def health(request: web.Request) -> web.Response:
    return web.json_response({'status': 'ok'})


async def process_dispatch_in(app: web.Application) -> None:
    """
    Consume traffic's dispatch-in stream, send each message over its
    channel (stub senders only), and record the outcome.
    """
    async for message in consume(app[RABBIT_KEY], 'dispatch-in'):
        sender = SENDERS[message['channel']]
        await sender.send(message['recipient'], message['body'])

        async with app[DB_KEY].begin() as conn:
            await conn.execute(
                messages_table.insert().values(
                    id=message['id'],
                    channel=message['channel'],
                    recipient=message['recipient'],
                    send_status='sent',
                    sent_at=datetime.now(UTC),
                )
            )


def build_app(config: Config) -> web.Application:
    app = make_app(config, routes=routes, db_dsn=config['db'])
    run_in_background(app, process_dispatch_in)
    return app
