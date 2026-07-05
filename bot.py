"""Terabox Downloader Bot — Main entry point.

Runs:
- Telegram bot (polling)
- KlikQRIS webhook server (port from config.WEBHOOK_PORT)
"""

import os
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters,
)

from config import config
from database.models import db
from database.migrations import migrate
from terabox.utils import check_url, extract_urls, format_size, get_file_icon
from terabox.resolver import resolve as resolve_terabox
from terabox.downloader import download_file, upload_to_telegram
from payments.handler import (
    bayar_command, pay_qris_callback, pay_status_callback,
    status_command as pay_status_command,
    vip_info_text,
)
from payments.webhook_server import start_webhook_server
from admin.handlers import (
    pending_command, approve_callback, reject_callback,
    vipadd_command, viprem_command, vips_command,
    stats_command, config_command, broadcast_command,
    approve_command, reject_command,
)

# ── SETUP ────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── USER COMMANDS ────────────────────────────────────

async def start(update: Update, context):
    """Handle /start — welcome + register user."""
    user = update.effective_user
    db.create_user(user.id, user.username, user.full_name)

    text = (
        f"👋 Halo <b>{user.first_name}</b>!\n\n"
        "🚀 <b>Terabox Downloader Bot</b>\n"
        "Kirim link Terabox, aku download-in!\n\n"
        "🔗 Format link yang didukung:\n"
        "• <code>terabox.com/s/xxxx</code>\n"
        "• <code>teraboxapp.com/s/xxxx</code>\n"
        "• <code>mirrobox.com/s/xxxx</code>\n"
        "• dan mirror lainnya\n\n"
        "Ketik /help untuk bantuan."
    )

    if config.VIP_ENABLED:
        if not db.is_vip(user.id):
            trial_info = ""
            if config.VIP_TRIAL_ENABLED:
                trial_info = f"\n🎁 Free trial: {config.VIP_TRIAL_DOWNLOADS}x download!"
            text += (
                f"\n\n💎 Butuh VIP untuk download.{trial_info}\n"
                "Ketik /vip untuk info langganan."
            )

    await update.message.reply_text(text, parse_mode="HTML")


async def help_command(update: Update, context):
    """Handle /help."""
    text = (
        "📖 <b>Bantuan Terabox Downloader</b>\n\n"
        "1️⃣ Kirim link Terabox\n"
        "2️⃣ Bot akan resolve & download\n"
        "3️⃣ File dikirim ke kamu\n\n"
        "<b>📋 Perintah:</b>\n"
        "/start — Mulai bot\n"
        "/help — Bantuan ini\n"
        "/vip — Info langganan VIP\n"
        "/bayar — Beli VIP via QRIS\n"
        "/status — Cek status akun & VIP\n\n"
        "<b>💳 Pembayaran:</b>\n"
        "• Otomatis via KlikQRIS\n"
        "• Scan QR → Bayar → VIP langsung aktif!"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def vip_command(update: Update, context):
    """Handle /vip — show VIP info with pay button."""
    if not config.VIP_ENABLED:
        await update.message.reply_text(
            "VIP tidak diaktifkan. Semua download gratis! 🎉"
        )
        return

    user_id = update.effective_user.id
    if db.is_vip(user_id):
        remaining = db.get_remaining_days(user_id)
        dur = "Lifetime ♾️" if remaining is None else f"{remaining} hari lagi"
        await update.message.reply_text(
            f"💎 Kamu sudah <b>VIP</b>!\n⏳ Masa aktif: {dur}",
            parse_mode="HTML",
        )
        return

    await update.message.reply_text(
        vip_info_text(),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Bayar via QRIS", callback_data="pay_qris")],
            [InlineKeyboardButton("ℹ️ Cek Status", callback_data="pay_status")],
        ]),
    )


# ── MAIN LINK HANDLER ────────────────────────────────

async def handle_link(update: Update, context):
    """Process Terabox link from user message."""
    user_id = update.effective_user.id
    text = update.message.text

    # Check if message contains terabox link
    url = extract_urls(text)
    if not url:
        return

    # Register user if new
    db.create_user(
        user_id, update.effective_user.username, update.effective_user.full_name
    )

    # ── VIP CHECK ──
    if config.VIP_ENABLED and not db.is_vip(user_id):
        if config.VIP_TRIAL_ENABLED:
            used = db.get_free_downloads_used(user_id)
            if used >= config.VIP_TRIAL_DOWNLOADS:
                await update.message.reply_text(
                    f"⛔ <b>Trial habis!</b>\n\n"
                    f"Kamu sudah pakai {used}/{config.VIP_TRIAL_DOWNLOADS} download gratis.\n"
                    "Ketik /vip untuk beli akses.",
                    parse_mode="HTML",
                )
                return
        else:
            await update.message.reply_text(
                "⛔ <b>VIP Required</b>\n\nKetik /vip untuk info langganan.",
                parse_mode="HTML",
            )
            return

    # ── PROCESS ──
    status_msg = await update.message.reply_text("🔍 Memproses link...")

    result = await resolve_terabox(url)

    if not result["success"]:
        await status_msg.edit_text(
            f"❌ <b>Gagal resolve link</b>\n\n"
            f"{result.get('error', 'Unknown error')}\n\n"
            "Coba lagi nanti atau cek apakah link valid.",
            parse_mode="HTML",
        )
        return

    # Build info message
    file_name = result["file_name"] or "Unknown"
    file_size = result["size"] or "Unknown"
    ext = os.path.splitext(file_name)[1] if file_name else ""
    icon = get_file_icon(ext)
    sizebytes = result.get("sizebytes", 0)

    await status_msg.edit_text(
        f"{icon} <b>{file_name}</b>\n"
        f"📦 <b>{file_size}</b>\n"
        f"🔗 Strategi: {result['strategy_used']}",
        parse_mode="HTML",
    )

    # Check if file is too large for Telegram
    max_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024

    if sizebytes and sizebytes > max_bytes:
        await update.message.reply_text(
            f"⚠️ File terlalu besar untuk Telegram (>{config.MAX_FILE_SIZE_MB} MB).\n\n"
            f"🔗 <b>Download langsung:</b>\n"
            f"<a href='{result['direct_link']}'>Klik di sini</a>\n\n"
            "⏰ Link berlaku terbatas. Download sekarang!",
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
        db.add_download_count(user_id)
        return

    # Download + Upload
    progress_msg = await update.message.reply_text("⬇️ Mendownload...")

    async def dl_progress(downloaded, total):
        pct = int(downloaded / total * 100) if total else 0
        try:
            await progress_msg.edit_text(f"⬇️ Mendownload... {pct}%")
        except Exception:
            pass

    file_path = await download_file(
        result["direct_link"],
        file_name,
        progress_callback=dl_progress if sizebytes else None,
    )

    if not file_path:
        await progress_msg.edit_text("❌ Gagal mendownload file.")
        return

    await progress_msg.edit_text("📤 Mengupload ke Telegram...")

    caption = f"{icon} {file_name}\n📦 {file_size}"
    success = await upload_to_telegram(
        context.bot, user_id, file_path, file_name,
        file_size=sizebytes, caption=caption,
    )

    if success:
        await progress_msg.delete()
        db.add_download_count(user_id)
    else:
        await progress_msg.edit_text(
            f"⚠️ Upload gagal (file mungkin terlalu besar).\n\n"
            f"🔗 Download langsung:\n{result['direct_link']}"
        )


# ── MAIN ─────────────────────────────────────────────

async def main():
    """Start the bot + webhook server."""
    # Validate config
    missing = config.validate()
    if missing:
        logger.error(f"Missing config: {', '.join(missing)}")
        logger.info("Set BOT_TOKEN + ADMIN_IDS in .env to start.")
        return

    # Initialize database
    migrate(config.db_path())
    db.init()
    logger.info("Database initialized")

    # Build Telegram app
    app = Application.builder().token(config.BOT_TOKEN).build()

    # -- User commands --
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("vip", vip_command))
    app.add_handler(CommandHandler("bayar", bayar_command))
    app.add_handler(CommandHandler("status", pay_status_command))

    # -- Admin commands --
    app.add_handler(CommandHandler("pending", pending_command))
    app.add_handler(CommandHandler("approve", approve_command))
    app.add_handler(CommandHandler("reject", reject_command))
    app.add_handler(CommandHandler("vipadd", vipadd_command))
    app.add_handler(CommandHandler("viprem", viprem_command))
    app.add_handler(CommandHandler("vips", vips_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("config", config_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    # -- Inline callbacks --
    app.add_handler(CallbackQueryHandler(pay_qris_callback, pattern="^pay_qris$"))
    app.add_handler(CallbackQueryHandler(pay_status_callback, pattern=r"^pay_status$|^checkpay_"))
    app.add_handler(CallbackQueryHandler(approve_callback, pattern=r"^appr_\d+"))
    app.add_handler(CallbackQueryHandler(reject_callback, pattern=r"^rej_\d+"))

    # -- Link handler --
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_link,
    ))

    # Start webhook server (non-blocking)
    runner = await start_webhook_server(app.bot)
    logger.info(f"Webhook server on port {config.WEBHOOK_PORT}")
    logger.info(f"Webhook URL: {config.WEBHOOK_HOST}/webhook/klikqris")

    # Start bot polling
    logger.info("Bot polling started...")
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        # Keep running
        await asyncio.Event().wait()
    finally:
        await app.stop()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
