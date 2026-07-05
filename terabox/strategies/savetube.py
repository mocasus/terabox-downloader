"""Strategy 1: ytshorts.savetube.me API — no cookie needed (primary)."""

import logging
import re

import aiohttp

from terabox.utils import find_between, format_size

logger = logging.getLogger(__name__)

__all__ = ["resolve"]


async def resolve(url: str, session: aiohttp.ClientSession = None) -> dict | None:
    """
    Resolve Terabox URL via savetube proxy.
    Returns dict with file metadata or None on failure.
    """
    own_session = session is None
    if own_session:
        session = aiohttp.ClientSession()

    try:
        # Step 1: GET page to extract thumbnail
        netloc = urlparse_netloc(url)
        page_url = url.replace(netloc, "1024terabox.com")

        async with session.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()
            thumb = find_between(html, 'og:image" content="', '"')

        # Step 2: POST to savetube API
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://ytshorts.savetube.me",
            "Sec-Fetch-Site": "same-origin",
        }

        async with session.post(
            "https://ytshorts.savetube.me/api/v1/terabox-downloader",
            headers=headers,
            json={"url": url},
            timeout=aiohttp.ClientTimeout(total=20),
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

        responses = data.get("response", [])
        if not responses:
            return None

        resolutions = responses[0].get("resolutions", {})
        if not resolutions:
            return None

        fast_dl = resolutions.get("Fast Download", "")
        hd_video = resolutions.get("HD Video", "")

        if not hd_video:
            return None

        # Step 3: HEAD HD Video to get size + filename
        file_name = None
        size_bytes = 0

        async with session.head(
            hd_video,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=aiohttp.ClientTimeout(total=10),
            allow_redirects=True,
        ) as resp:
            content_length = resp.headers.get("Content-Length", 0)
            if content_length:
                size_bytes = int(content_length)
            disposition = resp.headers.get("content-disposition", "")
            if disposition:
                match = re.findall(r'filename="?(.+?)"?$', disposition)
                if match:
                    file_name = match[0]

        # Step 4: Follow Fast Download redirect → direct link
        direct_link = None
        async with session.head(
            fast_dl,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=aiohttp.ClientTimeout(total=10),
            allow_redirects=False,
        ) as resp:
            direct_link = resp.headers.get("Location", fast_dl)

        return {
            "file_name": file_name,
            "link": hd_video,
            "direct_link": direct_link or fast_dl,
            "thumb": thumb,
            "size": format_size(size_bytes) if size_bytes else "Unknown",
            "sizebytes": size_bytes,
            "strategy": "savetube",
        }

    except Exception:
        return None
    finally:
        if own_session:
            await session.close()


def urlparse_netloc(url: str) -> str:
    """Extract netloc from URL."""
    from urllib.parse import urlparse
    return urlparse(url).netloc
