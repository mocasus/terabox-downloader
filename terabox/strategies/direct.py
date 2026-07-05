"""Strategy 3: Direct cookie-based resolution (ndus cookie)."""
import aiohttp


async def resolve(url: str, session: aiohttp.ClientSession = None) -> dict | None:
    """
    Direct resolution using ndus cookie — last resort.
    Requires valid cookie in environment/config.
    """
    return None  # Not yet implemented
