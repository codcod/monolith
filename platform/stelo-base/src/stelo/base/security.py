import logging
import uuid

from aiohttp import web

logger = logging.getLogger(__name__)

REQUEST_ID_KEY = web.RequestKey('request_id', str)


@web.middleware
async def request_id_middleware(request: web.Request, handler):
    """
    Stamp every request with an id (reusing an inbound one if present) so
    it can be correlated across modules in logs.
    """
    request_id = request.headers.get('X-Request-Id', str(uuid.uuid4()))
    request[REQUEST_ID_KEY] = request_id
    response = await handler(request)
    response.headers['X-Request-Id'] = request_id
    return response


def auth_middleware(token: str):
    """
    Build a bearer-token check middleware. `token` comes from module
    config. This is a stub seam, not a real auth system: no issuing,
    rotation, or per-client scopes.
    """

    @web.middleware
    async def _auth(request: web.Request, handler):
        if request.path == '/health':
            return await handler(request)
        if request.headers.get('Authorization') != f'Bearer {token}':
            raise web.HTTPUnauthorized()
        return await handler(request)

    return _auth
