"""Terabox Downloader Bot — Configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from .env"""

    # === Bot ===
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [
        int(x.strip())
        for x in os.getenv("ADMIN_IDS", "").split(",")
        if x.strip()
    ]

    # === VIP ===
    VIP_ENABLED: bool = os.getenv("VIP_ENABLED", "false").lower() == "true"
    VIP_PRICE: int = int(os.getenv("VIP_PRICE", "15000"))
    VIP_DURATION_DAYS: int = int(os.getenv("VIP_DURATION_DAYS", "30"))
    VIP_TRIAL_ENABLED: bool = os.getenv("VIP_TRIAL_ENABLED", "false").lower() == "true"
    VIP_TRIAL_DOWNLOADS: int = int(os.getenv("VIP_TRIAL_DOWNLOADS", "3"))

    # === KlikQRIS ===
    KLIKQRIS_API_KEY: str = os.getenv("KLIKQRIS_API_KEY", "")
    KLIKQRIS_MERCHANT_ID: str = os.getenv("KLIKQRIS_MERCHANT_ID", "")
    KLIKQRIS_WEBHOOK_SECRET: str = os.getenv("KLIKQRIS_WEBHOOK_SECRET", "")
    KLIKQRIS_SANDBOX: bool = os.getenv("KLIKQRIS_SANDBOX", "false").lower() == "true"

    # === Webhook Server ===
    WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", "")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8000"))

    # === Download ===
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    CONCURRENT_DOWNLOADS: int = int(os.getenv("CONCURRENT_DOWNLOADS", "3"))
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "/tmp/terabox")

    # === Database ===
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data.db")

    @staticmethod
    def db_path() -> str:
        """Extract file path from DATABASE_URL."""
        url = Config.DATABASE_URL
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "")
        return url

    @staticmethod
    def validate() -> list[str]:
        """Check required config. Returns list of missing keys."""
        missing = []
        if not Config.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not Config.ADMIN_IDS:
            missing.append("ADMIN_IDS")
        if Config.VIP_ENABLED:
            if not Config.KLIKQRIS_API_KEY:
                missing.append("KLIKQRIS_API_KEY")
            if not Config.KLIKQRIS_MERCHANT_ID:
                missing.append("KLIKQRIS_MERCHANT_ID")
        return missing

    @staticmethod
    def klikqris_base_url() -> str:
        """Return KlikQRIS API base URL (sandbox or production)."""
        if Config.KLIKQRIS_SANDBOX:
            return "https://klikqris.com/api/sandbox"
        return "https://klikqris.com/api"


config = Config()
