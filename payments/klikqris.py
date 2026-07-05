"""KlikQRIS Payment Gateway Integration — Dynamic QRIS + Webhook Callback.

Flow:
1. User runs /bayar → bot creates transaction via KlikQRIS API
2. Bot sends QR image to user → user scans & pays
3. KlikQRIS sends webhook → webhook server auto-activates VIP
4. Bot notifies user instantly

API ref: https://klikqris.com/dokumentasi-api
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime

import aiohttp

from config import config

logger = logging.getLogger(__name__)


# ── KlikQRIS API Client ───────────────────────────

async def _api(method: str, endpoint: str, data: dict | None = None) -> dict:
    """Make authenticated request to KlikQRIS API."""
    url = f"{config.klikqris_base_url()}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config.KLIKQRIS_API_KEY,
        "id_merchant": config.KLIKQRIS_MERCHANT_ID,
    }

    async with aiohttp.ClientSession() as session:
        if method == "POST":
            async with session.post(url, json=data, headers=headers) as resp:
                return await resp.json()
        elif method == "GET":
            async with session.get(url, headers=headers) as resp:
                return await resp.json()
        else:
            raise ValueError(f"Unsupported method: {method}")


async def create_transaction(
    order_id: str,
    amount: int,
    keterangan: str = "",
) -> dict:
    """
    Create a new QRIS transaction.

    Args:
        order_id: Unique order ID (e.g., VIP-123456789-1690000000)
        amount: Payment amount in IDR
        keterangan: Optional description

    Returns:
        {
            "success": True,
            "order_id": "VIP-...",
            "total_amount": 15021.00,   # with unique code
            "qris_url": "https://...png",  # QR image URL
            "qris_image": "base64...",     # base64 QR image
            "expired_at": "2026-...",
            "signature": "...",
        }
    """
    try:
        payload = {
            "order_id": order_id,
            "amount": amount,
            "id_merchant": config.KLIKQRIS_MERCHANT_ID,
            "keterangan": keterangan,
        }

        result = await _api("POST", "/qris/create", payload)

        if result.get("status") and result.get("data"):
            d = result["data"]
            return {
                "success": True,
                "order_id": d["order_id"],
                "total_amount": float(d["total_amount"]),
                "qris_url": d.get("qris_url", ""),
                "qris_image": d.get("qris_image", ""),
                "expired_at": d.get("expired_at", ""),
                "expired_menit": d.get("expired_menit", "60"),
                "signature": d.get("signature", ""),
                "raw": d,
            }
        else:
            logger.error(f"KlikQRIS create failed: {result}")
            return {"success": False, "error": result.get("message", "Unknown error")}

    except Exception as e:
        logger.exception("KlikQRIS create_transaction error")
        return {"success": False, "error": str(e)}


async def check_status(order_id: str) -> dict:
    """
    Check transaction status.

    Returns:
        {
            "success": True,
            "status": "PENDING" | "SUCCESS" | "EXPIRED",
            "paid_at": "..." or None,
            ...
        }
    """
    try:
        result = await _api("GET", f"/qris/status/{order_id}")

        if result.get("status") and result.get("data"):
            d = result["data"]
            return {
                "success": True,
                "order_id": d["order_id"],
                "status": d.get("status", "PENDING"),
                "total_amount": float(d.get("total_amount", 0)),
                "paid_at": d.get("paid_at"),
                "expired_at": d.get("expired_at"),
                "signature": d.get("signature", ""),
                "raw": d,
            }
        else:
            return {"success": False, "error": result.get("message", "Unknown error")}

    except Exception as e:
        logger.exception("KlikQRIS check_status error")
        return {"success": False, "error": str(e)}


def verify_signature(received_signature: str, stored_signature: str) -> bool:
    """Verify webhook signature against stored signature from creation."""
    if not stored_signature:
        return False
    return hmac.compare_digest(received_signature, stored_signature)


def generate_order_id(user_id: int) -> str:
    """Generate unique order ID: VIP-{user_id}-{timestamp}"""
    ts = int(datetime.now().timestamp())
    return f"VIP-{user_id}-{ts}"


# ── KlikQRIS Class Wrapper ──────────────────────────

class KlikQRIS:
    """KlikQRIS payment gateway client.

    Usage:
        qris = KlikQRIS()
        result = await qris.create(amount=15000, user_id=123)
        status = await qris.check(order_id)
    """

    # Re-exports for backward compat
    create_transaction = staticmethod(create_transaction)
    check_status = staticmethod(check_status)
    verify_signature = staticmethod(verify_signature)
    generate_order_id = staticmethod(generate_order_id)

    @staticmethod
    async def create(amount: int, user_id: int, description: str = "") -> dict:
        """Quick create: generate order_id + create transaction."""
        order_id = generate_order_id(user_id)
        return await create_transaction(
            order_id=order_id,
            amount=amount,
            keterangan=description or f"VIP — {user_id}",
        )

    @staticmethod
    async def check(order_id: str) -> dict:
        """Check transaction status."""
        return await check_status(order_id)
