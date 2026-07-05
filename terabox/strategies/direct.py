"""Strategy 3: Direct cookie-based resolution (ndus cookie)."""

import logging

import aiohttp

logger = logging.getLogger(__name__)

__all__ = ["resolve"]


async def resolve(url: str, session: aiohttp.ClientSession = None) -> dict | None:
    """
    Direct resolution using ndus cookie — last resort.
    Requires valid cookie in environment/config.
    """
    return None  # Not yet implemented
