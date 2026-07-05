"""Terabox downloader utilities."""
import re
from urllib.parse import urlparse, parse_qs

TERABOX_PATTERNS = [
    r"terabox\.app",
    r"terabox\.com",
    r"www\.terabox\.ap",
    r"www\.terabox\.com",
    r"1024terabox\.com",
    r"www\.1024tera\.co",
    r"1024tera\.com",
    r"teraboxlink\.com",
    r"teraboxshare\.com",
    r"teraboxapp\.com",
    r"www\.teraboxapp\.com",
    r"terasharefile\.com",
    r"terafileshare\.com",
    r"terasharelink\.com",
    r"mirrobox\.com",
    r"www\.mirrobox\.com",
    r"nephobox\.com",
    r"www\.nephobox\.com",
    r"freeterabox\.com",
    r"www\.freeterabox\.com",
    r"4funbox\.com",
    r"www\.4funbox\.com",
    r"momerybox\.com",
    r"www\.momerybox\.com",
    r"tibibox\.com",
    r"www\.tibibox\.com",
]


def check_url(url: str) -> bool:
    """Check if URL is a valid Terabox link."""
    if not url:
        return False
    for pattern in TERABOX_PATTERNS:
        if re.search(pattern, url):
            return True
    return False


def extract_urls(text: str) -> str | None:
    """Extract first Terabox URL from text."""
    pattern = r"(https?://\S+)"
    urls = re.findall(pattern, text)
    for url in urls:
        if check_url(url):
            return url
    return None


def extract_surl(url: str) -> str | None:
    """Extract 'surl' parameter from Terabox URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get("surl", [None])[0]


def find_between(data: str, first: str, last: str) -> str | None:
    """Find text between two substrings."""
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return None


def format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    if not size_bytes:
        return "Unknown"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def get_file_icon(ext: str) -> str:
    """Return emoji icon based on file extension."""
    icons = {
        ".mp4": "🎬", ".mkv": "🎬", ".avi": "🎬", ".mov": "🎬",
        ".mp3": "🎵", ".wav": "🎵", ".flac": "🎵",
        ".jpg": "🖼️", ".jpeg": "🖼️", ".png": "🖼️", ".gif": "🖼️",
        ".pdf": "📄", ".doc": "📝", ".docx": "📝",
        ".zip": "📦", ".rar": "📦", ".7z": "📦",
        ".apk": "📱", ".exe": "💻",
    }
    ext = ext.lower()
    if not ext.startswith("."):
        ext = f".{ext}"
    return icons.get(ext, "📁")
