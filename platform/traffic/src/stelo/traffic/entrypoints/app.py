import typing as tp

from aiohttp import web
from stelo.base.config import Config
from stelo.base.messages import Message as WireMessage
from stelo.base.streams import consume
from stelo.base.streams import publish as stream_publish
from stelo.base.webapp import DB_KEY, RABBIT_KEY, make_app, run_in_background
from stelo.traffic.service_layer import services
from stelo.traffic.service_layer.unit_of_work import TrafficUnitOfWork

routes = web.RouteTableDef()


@routes.get('/health')
async def health(request: web.Request) -> web.Response:
    return web.json_response({'status': 'ok'})


async def process_traffic_in(app: web.Application) -> None:
    """
    Consume inbox's traffic-in stream and hand each message to the service
    layer, which records a routing row and republishes to dispatch-in.
    """

    async def publish(message: WireMessage) -> None:
        await stream_publish(app[RABBIT_KEY], 'dispatch-in', message)

    async for raw in consume(app[RABBIT_KEY], 'traffic-in'):
        message = tp.cast(WireMessage, raw)
        uow = TrafficUnitOfWork(app[DB_KEY])
        await services.route_message(message, uow, publish)


def build_app(config: Config) -> web.Application:
    app = make_app(config, routes=routes, db_dsn=config['db'])
    run_in_background(app, process_traffic_in)
    return app
