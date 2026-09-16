import typing as tp

from aiohttp import web
from stelo.base.channels import SENDERS
from stelo.base.config import Config
from stelo.base.messages import Message as WireMessage
from stelo.base.streams import consume
from stelo.base.webapp import DB_KEY, RABBIT_KEY, make_app, run_in_background

from stelo.dispatcher.service_layer import services
from stelo.dispatcher.service_layer.unit_of_work import DispatcherUnitOfWork

routes = web.RouteTableDef()


@routes.get("/health")
async def health(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def process_dispatch_in(app: web.Application) -> None:
    """
    Consume traffic's dispatch-in stream and hand each message to the
    service layer, which sends it (stub sender) and records the outcome.
    """
    async for raw in consume(app[RABBIT_KEY], "dispatch-in"):
        message = tp.cast(WireMessage, tp.cast(object, raw))
        sender = SENDERS[message["channel"]]
        uow = DispatcherUnitOfWork(app[DB_KEY])
        await services.dispatch_message(message, uow, sender)


def build_app(config: Config) -> web.Application:
    app = make_app(config, routes=routes, db_dsn=config["db"])
    run_in_background(app, process_dispatch_in)
    return app
