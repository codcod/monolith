import asyncio

# from stelo import inbox
from .config import Config

async def run_module(config: Config) -> None:
    """
    Start, configure, and run Traffic module.
    """
    while True:
        print('Traffic hearbeat')
        await asyncio.sleep(1)