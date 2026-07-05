"""File downloader — stream from URL, upload to Telegram."""

import logging
import os
import asyncio

import aiohttp
import aiofiles

from config import config

logger = logging.getLogger(__name__)

__all__ = ["download_file", "upload_to_telegram"]


async def download_file(url: str, file_name: str, progress_callback=None) -> str | None:
    """
    Download file from URL to config.DOWNLOAD_DIR.
    Returns local file path or None on failure.
    """
    os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)

    # Sanitize filename
    safe_name = file_name.replace("/", "_").replace("\\", "_") if file_name else "download"
    file_path = os.path.join(config.DOWNLOAD_DIR, safe_name)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status != 200:
                    return None

                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0

                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 64):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total:
                            await progress_callback(downloaded, total)

        return file_path

    except Exception:
        # Cleanup partial download
        if os.path.exists(file_path):
            os.remove(file_path)
        return None


async def upload_to_telegram(bot, chat_id: int, file_path: str, file_name: str,
                              file_size: int, thumb_url: str = None,
                              caption: str = None, progress_callback=None) -> bool:
    """
    Upload file to Telegram chat. Returns True on success.
    Handles size limit check.
    """
    max_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024

    if file_size > max_bytes:
        return False  # File too large, caller should send direct link instead

    try:
        # Determine file type for proper upload
        ext = os.path.splitext(file_name)[1].lower()
        video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"}
        audio_exts = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
        doc_exts = {".pdf", ".zip", ".rar", ".7z", ".apk", ".exe", ".doc", ".docx"}

        with open(file_path, "rb") as f:
            if ext in video_exts:
                await bot.send_video(
                    chat_id=chat_id,
                    video=f,
                    caption=caption,
                    supports_streaming=True,
                )
            elif ext in audio_exts:
                await bot.send_audio(
                    chat_id=chat_id,
                    audio=f,
                    caption=caption,
                )
            elif ext in doc_exts:
                await bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=caption,
                )
            else:
                # Generic: try document
                await bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=caption,
                )

        return True

    except Exception:
        return False
    finally:
        # Cleanup temp file
        try:
            os.remove(file_path)
        except OSError:
            pass
