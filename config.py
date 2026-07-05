# Terabox Downloader Bot - Configuration
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from .env"""

    # === Bot ===
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    ]

    # === VIP ===
    VIP_ENABLED: bool = os.getenv("VIP_ENABLED", "false").lower() == "true"
    VIP_PRICE: int = int(os.getenv("VIP_PRICE", "15000"))
    VIP_DURATION_DAYS: int = int(os.getenv("VIP_DURATION_DAYS", "30"))
    VIP_TRIAL_ENABLED: bool = os.getenv("VIP_TRIAL_ENABLED", "false").lower() == "true"
    VIP_TRIAL_DOWNLOADS: int = int(os.getenv("VIP_TRIAL_DOWNLOADS", "3"))

    # === Payment ===
    PAYMENT_METHOD: str = os.getenv("PAYMENT_METHOD", "manual")
    PAYMENT_QRIS_IMAGE: str = os.getenv("PAYMENT_QRIS_IMAGE", "assets/qris.jpg")
    PAYMENT_CALLBACK_SECRET: str = os.getenv("PAYMENT_CALLBACK_SECRET", "")

    # === Download ===
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    CONCURRENT_DOWNLOADS: int = int(os.getenv("CONCURRENT_DOWNLOADS", "3"))
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "/tmp/terabox")

    # === Database ===
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data.db")

    @classmethod
    def db_path(cls) -> str:
        """Extract file path from sqlite:/// URL"""
        return cls.DATABASE_URL.replace("sqlite:///", "")

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required config, returns list of missing vars"""
        missing = []
        if not cls.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not cls.ADMIN_IDS:
            missing.append("ADMIN_IDS")
        return missing


config = Config()
