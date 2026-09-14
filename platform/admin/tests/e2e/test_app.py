from aiohttp.test_utils import TestClient, TestServer
from stelo.admin.entrypoints.app import build_app


def _config() -> dict:
    return {'db': 'postgresql+asyncpg://stelo:stelo@postgres/stelo'}


async def test_health_ok():
    async with TestClient(TestServer(build_app(_config()))) as client:
        resp = await client.get('/health')
        assert resp.status == 200


async def test_index_page_is_reachable_without_auth():
    async with TestClient(TestServer(build_app(_config()))) as client:
        resp = await client.get('/')
        assert resp.status == 200
        assert 'Relay Console' in await resp.text()


async def test_static_datastar_bundle_is_reachable_without_auth():
    async with TestClient(TestServer(build_app(_config()))) as client:
        resp = await client.get('/static/datastar.js')
        assert resp.status == 200
