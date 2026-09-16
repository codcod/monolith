import logging
import time
import tomllib
import typing as tp

import uvloop


class Config(tp.TypedDict):
    """
    A module's own section of its `config.toml` (e.g. `config["traffic"]`
    after `read_config`) — the shape `make_app`/`build_app` expect. `db` is
    the one key every module's config carries; the rest are per-module
    (e.g. admin has no `rabbitmq_url`/`auth_token`).
    """

    db: str
    rabbitmq_url: tp.NotRequired[str]
    auth_token: tp.NotRequired[str]
    log_level: tp.NotRequired[str]
    workers: tp.NotRequired[int]


def read_config(fn: str) -> dict[str, Config]:
    """
    Read configuration file and return configuration object, keyed by
    module name (each module's config.toml has one top-level table).
    """
    with open(fn, "rb") as f:
        return tomllib.load(f)


def setup_logging(config: Config) -> None:
    """
    Setup logging for an application.
    """
    level = logging.getLevelNamesMapping().get(
        config.get("log_level", "WARNING"), logging.WARNING
    )
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(module)s] %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S %Z",
        # Without force=True this is a no-op whenever the root logger
        # already has handlers (e.g. under pytest, or any host process
        # that configured logging first).
        force=True,
    )
    # UTC, not local time — containers shouldn't need a timezone package
    # just to log, and logs from every module line up on one clock.
    logging.Formatter.converter = time.gmtime


def setup_app(config: Config) -> None:
    """
    Setup Stelo application.

    1. Setup logging.
    2. Install uvloop based asyncio loop.
    """
    setup_logging(config)
    uvloop.install()  # pyright: ignore[reportAny] -- deprecated dynamic shim, untyped in uvloop's own stubs
