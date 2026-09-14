from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from stelo.base.security import REQUEST_ID_KEY, auth_middleware, request_id_middleware


def _make_client() -> TestClient:
    app = web.Application(
        middlewares=[request_id_middleware, auth_middleware('secret')]
    )

    async def health(request: web.Request) -> web.Response:
        return web.json_response({'ok': True})

    async def protected(request: web.Request) -> web.Response:
        return web.json_response({'request_id': request[REQUEST_ID_KEY]})

    app.router.add_get('/health', health)
    app.router.add_get('/protected', protected)
    return TestClient(TestServer(app))


async def test_health_bypasses_auth():
    async with _make_client() as client:
        resp = await client.get('/health')
        assert resp.status == 200


async def test_protected_requires_bearer_token():
    async with _make_client() as client:
        resp = await client.get('/protected')
        assert resp.status == 401

        resp = await client.get(
            '/protected', headers={'Authorization': 'Bearer secret'}
        )
        assert resp.status == 200


async def test_request_id_is_stamped_and_echoed():
    async with _make_client() as client:
        resp = await client.get(
            '/protected',
            headers={'Authorization': 'Bearer secret', 'X-Request-Id': 'abc'},
        )
        assert resp.status == 200
        assert resp.headers['X-Request-Id'] == 'abc'
        body = await resp.json()
        assert body['request_id'] == 'abc'
