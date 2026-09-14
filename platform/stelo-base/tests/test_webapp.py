from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from stelo.base.webapp import make_app

routes = web.RouteTableDef()


@routes.get('/thing')
async def thing(request: web.Request) -> web.Response:
    return web.json_response({'ok': True})


async def test_require_auth_defaults_to_protecting_routes():
    app = make_app({'auth_token': 'secret'}, routes=routes)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/thing')
        assert resp.status == 401


async def test_require_auth_false_leaves_routes_public():
    app = make_app({'auth_token': 'secret'}, routes=routes, require_auth=False)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get('/thing')
        assert resp.status == 200
