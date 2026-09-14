import logging
import time
import tomllib
import typing as tp

import uvloop

type Config = dict[tp.Any, tp.Any]


def read_config(fn: str) -> Config:
    """
    Read configuration file and return configuration object.
    """
    with open(fn, 'rb') as f:
        return tomllib.load(f)


def setup_logging(config: Config) -> None:
    """
    Setup logging for an application.
    """
    level = logging.getLevelNamesMapping().get(
        config.get('log_level', 'WARNING'), logging.WARNING
    )
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(module)s] %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S %Z',
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
    uvloop.install()
