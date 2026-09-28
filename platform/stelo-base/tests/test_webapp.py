import asyncio

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from stelo.base import webapp
from stelo.base.webapp import DB_KEY, RABBIT_KEY, make_app

routes = web.RouteTableDef()


@routes.get("/thing")
async def thing(request: web.Request) -> web.Response:
    return web.json_response({"ok": True})


async def test_require_auth_defaults_to_protecting_routes():
    app = make_app({"auth_token": "secret"}, routes=routes)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get("/thing")
        assert resp.status == 401


async def test_require_auth_false_leaves_routes_public():
    app = make_app({"auth_token": "secret"}, routes=routes, require_auth=False)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get("/thing")
        assert resp.status == 200


async def test_run_outbox_relay_publishes_the_payload_to_its_destination(monkeypatch):
    delivered: list = []
    published: list = []

    async def fake_run_relay(engine, table, deliver):
        await deliver({"destination": "s", "payload": '{"id": "1"}'})
        delivered.append((engine, table))

    async def fake_publish(client, stream, message):
        published.append((client, stream, message))

    monkeypatch.setattr(webapp, "run_relay", fake_run_relay)
    monkeypatch.setattr(webapp, "publish", fake_publish)
    app = web.Application()
    app[DB_KEY] = "engine"
    app[RABBIT_KEY] = "client"

    webapp.run_outbox_relay(app, "table")
    async with TestClient(TestServer(app)):
        await asyncio.sleep(0)  # let the background task run

    assert delivered == [("engine", "table")]
    assert published == [("client", "s", {"id": "1"})]
