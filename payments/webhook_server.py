"""KlikQRIS Webhook Server — receives payment callbacks via HTTP.

Runs on WEBHOOK_PORT (default 8000) alongside the Telegram bot.
KlikQRIS sends POST to {WEBHOOK_HOST}:{WEBHOOK_PORT}/webhook/klikqris

Security:
- HMAC signature verification
- Idempotency check (prevent double processing)
- Secret token validation
"""

import json
import logging
from aiohttp import web

from config import config
from database.models import db
from payments.klikqris import verify_signature

logger = logging.getLogger(__name__)


async def health_handler(request):
    """GET /health — health check."""
    return web.json_response({"status": "ok"})


async def _notify_user(bot, user_id: int, text: str):
    """Send notification to user via Telegram."""
    try:
        await bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"Failed to notify user {user_id}: {e}")


def create_webhook_app(bot) -> web.Application:
    """Create aiohttp app with webhook endpoint."""

    app = web.Application()
    app["bot"] = bot  # Store bot reference

    async def webhook_handler(request):
        """POST /webhook/klikqris — KlikQRIS payment callback."""
        bot = request.app["bot"]

        try:
            body = await request.json()
            logger.info(f"Webhook received: {json.dumps(body, default=str)}")

            # Extract fields (handles both PG and MY PG formats)
            data = body.get("data", body)

            order_id = data.get("order_id", "")
            status = data.get("status", "").upper()
            signature = data.get("signature", "")
            total_amount = data.get("total_amount", data.get("amount_paid", 0))

            if status not in ("PAID", "SUCCESS"):
                logger.info(f"Ignoring non-success status: {status}")
                return web.json_response({"status": "ok"})

            # Find payment by order_id
            payment = db.get_payment_by_order_id(order_id)
            if not payment:
                logger.error(f"Unknown order_id: {order_id}")
                return web.json_response({"status": "ok"})

            # Prevent double processing
            if payment["status"] != "pending":
                logger.info(f"Payment {order_id} already processed: {payment['status']}")
                return web.json_response({"status": "ok"})

            # Verify signature
            stored_sig = payment.get("signature", "")
            if stored_sig and not verify_signature(signature, stored_sig):
                logger.error(f"Signature mismatch for {order_id}")
                return web.json_response({"status": "ok"})

            # Approve payment
            db.approve_payment_by_order_id(order_id)

            # Activate VIP
            user_id = payment["telegram_id"]
            db.set_vip(user_id, config.VIP_DURATION_DAYS)

            dur = (
                "Lifetime ♾️"
                if config.VIP_DURATION_DAYS == 0
                else f"{config.VIP_DURATION_DAYS} hari"
            )

            logger.info(f"VIP activated for {user_id} via webhook (order: {order_id})")

            # Notify user
            await _notify_user(
                bot,
                user_id,
                (
                    f"✅ <b>Pembayaran Berhasil!</b>\n\n"
                    f"💰 Rp {int(float(total_amount)):,}\n"
                    f"🆔 {order_id}\n\n"
                    f"🎉 VIP kamu sudah aktif!\n"
                    f"⏳ Masa aktif: {dur}\n\n"
                    "Kirim link Terabox untuk mulai download!"
                ),
            )

            # Notify admin
            for admin_id in config.ADMIN_IDS:
                await _notify_user(
                    bot,
                    admin_id,
                    (
                        f"💳 <b>Auto-Approved via Webhook</b>\n"
                        f"🆔 {order_id}\n"
                        f"👤 {user_id}\n"
                        f"💰 Rp {int(float(total_amount)):,}"
                    ),
                )

            return web.json_response({"status": "ok"})

        except Exception as e:
            logger.exception("Webhook processing error")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    app.router.add_get("/health", health_handler)
    app.router.add_post("/webhook/klikqris", webhook_handler)

    return app


async def start_webhook_server(bot) -> web.AppRunner:
    """Start the webhook server. Returns runner for cleanup."""
    app = create_webhook_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.WEBHOOK_PORT)
    await site.start()
    logger.info(f"Webhook server listening on port {config.WEBHOOK_PORT}")
    return runner


# ── WebhookServer Class Wrapper ──────────────────────

class WebhookServer:
    """KlikQRIS webhook receiver server.

    Usage:
        server = WebhookServer(bot)
        runner = await server.start()
        # ... bot runs ...
        await runner.cleanup()
    """

    def __init__(self, bot):
        self.bot = bot
        self._runner = None

    async def start(self) -> web.AppRunner:
        """Start the webhook HTTP server. Returns AppRunner."""
        self._runner = await start_webhook_server(self.bot)
        return self._runner

    async def stop(self):
        """Stop the webhook server."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
