import typing as tp

from aiohttp import web
from stelo.base.config import Config
from stelo.base.messages import Message as WireMessage
from stelo.base.streams import consume
from stelo.base.webapp import (
    DB_KEY,
    RABBIT_KEY,
    make_app,
    run_in_background,
    run_outbox_relay,
)

from stelo.traffic.adapters.tables import outbox
from stelo.traffic.service_layer import services
from stelo.traffic.service_layer.uow import TrafficUnitOfWork

routes = web.RouteTableDef()


@routes.get("/health")
async def health(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def process_traffic_in(app: web.Application) -> None:
    """
    Consume inbox's traffic-in stream and hand each message to the service
    layer, which records a routing row and enqueues it for dispatch-in.
    """

    async for raw in consume(app[RABBIT_KEY], "traffic-in"):
        message = tp.cast(WireMessage, tp.cast(object, raw))
        uow = TrafficUnitOfWork(app[DB_KEY])
        await services.route_message(message, uow)


def build_app(config: Config) -> web.Application:
    app = make_app(config, routes=routes, db_dsn=config["db"])
    run_in_background(app, process_traffic_in)
    run_outbox_relay(app, outbox)
    return app
