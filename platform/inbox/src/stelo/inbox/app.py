import time
import uuid
from datetime import datetime

import sqlalchemy as sa
from aiohttp import web
from stelo.base.config import Config
from stelo.base.messages import Message
from stelo.base.streams import publish
from stelo.base.webapp import DB_KEY, RABBIT_KEY, make_app

messages_table = sa.table(
    'messages',
    sa.column('id'),
    sa.column('channel'),
    sa.column('recipient'),
    sa.column('body'),
    sa.column('received_at'),
    schema='inbox',
)

routes = web.RouteTableDef()


@routes.get('/health')
async def health(request: web.Request) -> web.Response:
    return web.json_response({'status': 'ok'})


@routes.post('/messages')
async def create_message(request: web.Request) -> web.Response:
    payload = await request.json()
    channel = payload.get('channel')
    recipient = payload.get('recipient')
    body = payload.get('body')
    if channel not in ('sms', 'email', 'whatsapp') or not recipient or not body:
        raise web.HTTPBadRequest(reason='channel, recipient and body are required')

    message: Message = {
        'id': str(uuid.uuid4()),
        'channel': channel,
        'recipient': recipient,
        'body': body,
        'status': 'received',
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }

    async with request.app[DB_KEY].begin() as conn:
        await conn.execute(
            messages_table.insert().values(
                id=message['id'],
                channel=message['channel'],
                recipient=message['recipient'],
                body=message['body'],
                received_at=datetime.fromisoformat(message['created_at']),
            )
        )

    await publish(request.app[RABBIT_KEY], 'traffic-in', message)

    return web.json_response({'id': message['id']}, status=202)


def build_app(config: Config) -> web.Application:
    return make_app(config, routes=routes, db_dsn=config['db'])
