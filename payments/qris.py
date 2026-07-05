"""QRIS payment integration — static or dynamic QR."""
from config import config


def get_qris_image_path() -> str:
    """Return path to QRIS image file."""
    return config.PAYMENT_QRIS_IMAGE


def generate_qris(amount: int, label: str = "VIP") -> str:
    """
    Generate QRIS payment code.
    Currently returns static image path.
    Extend with Tripay/Xendit API for dynamic QR.
    """
    return get_qris_image_path()
