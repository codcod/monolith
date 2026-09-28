import typing as tp

import uvloop
from monobase.config import setup_logging


class Config(tp.TypedDict):
    """
    A module's own section of its `config.toml` (e.g. `config["traffic"]`
    after `monobase.config.read_config`) — the shape `make_app`/`build_app`
    expect. `db` is the one key every module's config carries; the rest are
    per-module (e.g. admin has no `rabbitmq_url`/`auth_token`).
    """

    db: str
    rabbitmq_url: tp.NotRequired[str]
    auth_token: tp.NotRequired[str]
    log_level: tp.NotRequired[str]
    workers: tp.NotRequired[int]


def setup_app(config: Config) -> None:
    """
    Setup Stelo application.

    1. Setup logging.
    2. Install uvloop based asyncio loop.
    """
    setup_logging(config.get("log_level"))
    uvloop.install()  # pyright: ignore[reportAny] -- deprecated dynamic shim, untyped in uvloop's own stubs
