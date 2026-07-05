"""Terabox URL resolution and file download pipeline.

Package structure:
- resolver: Multi-strategy engine with auto-fallback
- downloader: Async stream download + Telegram upload
- utils: URL parsing, size formatting, file icons
- strategies/: Individual resolution strategies
"""

from .resolver import resolve
from .downloader import download_file, upload_to_telegram
from .utils import extract_urls, check_url, format_size, get_file_icon

__all__ = [
    "resolve",
    "download_file",
    "upload_to_telegram",
    "extract_urls",
    "check_url",
    "format_size",
    "get_file_icon",
]
