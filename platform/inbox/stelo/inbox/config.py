import logging
import tomllib
import time
import typing as tp
import uvloop

Config: tp.TypeAlias = dict[tp.Any, tp.Any]

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
    level = logging.getLevelName(config.get('log_level', logging.WARNING))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(module)s] %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S %Z",
    )
    logging.Formatter.converter = time.localtime

def setup_app(config: Config) -> None:
    """
    Setup Stelo application.

    1. Setup logging.
    2. Install uvloop based asyncio loop.
    """
    setup_logging(config)
    uvloop.install()