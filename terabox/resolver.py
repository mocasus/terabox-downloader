"""Multi-strategy Terabox URL resolver with auto-fallback."""
import aiohttp
from terabox.strategies import savetube, publicearn, direct

STRATEGIES = [
    ("savetube", savetube.resolve),
    ("publicearn", publicearn.resolve),
    ("direct", direct.resolve),
]


async def resolve(url: str) -> dict:
    """
    Resolve a Terabox URL through all available strategies.
    Returns:
        {
            "success": bool,
            "file_name": str | None,
            "link": str | None,
            "direct_link": str | None,
            "thumb": str | None,
            "size": str | None,
            "sizebytes": int | None,
            "strategy_used": str | None,
            "error": str | None,
        }
    """
    result = {
        "success": False,
        "file_name": None,
        "link": None,
        "direct_link": None,
        "thumb": None,
        "size": None,
        "sizebytes": None,
        "strategy_used": None,
        "error": None,
    }

    async with aiohttp.ClientSession() as session:
        for name, strategy_fn in STRATEGIES:
            try:
                data = await strategy_fn(url, session)
                if data:
                    result.update(data)
                    result["success"] = True
                    result["strategy_used"] = name
                    return result
            except Exception as e:
                continue

    result["error"] = "All resolution strategies failed"
    return result
