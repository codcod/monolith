from aiohttp import web
from stelo.base.config import Config
from stelo.base.messages import Message as WireMessage
from stelo.base.streams import publish as stream_publish
from stelo.base.webapp import DB_KEY, RABBIT_KEY, make_app
from stelo.inbox.service_layer import services
from stelo.inbox.service_layer.unit_of_work import InboxUnitOfWork

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

    async def publish(message: WireMessage) -> None:
        await stream_publish(request.app[RABBIT_KEY], 'traffic-in', message)

    uow = InboxUnitOfWork(request.app[DB_KEY])
    message = await services.submit_message(channel, recipient, body, uow, publish)

    return web.json_response({'id': message.id}, status=202)


def build_app(config: Config) -> web.Application:
    return make_app(config, routes=routes, db_dsn=config['db'])
