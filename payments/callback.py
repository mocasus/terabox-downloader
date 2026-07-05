"""Payment callback webhook — auto-verify from payment gateway (stub)."""
from config import config


async def handle_callback(data: dict) -> dict | None:
    """
    Handle incoming payment callback from Tripay/Xendit/etc.
    Returns {"success": True, "user_id": int} or None.
    """
    return None  # Not yet implemented
