"""Terabox Downloader Bot — Main entry point."""
import os
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ConversationHandler,
)

from config import config
from database import db, migrate
from terabox.utils import check_url, extract_urls, format_size, get_file_icon
from terabox.resolver import resolve as resolve_terabox
from terabox.downloader import download_file, upload_to_telegram
from payments.handler import handle_payment, format_vip_info
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

# Conversation states
AWAIT_PROOF = 1


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
        "• terabox.com/s/xxxx\n"
        "• teraboxapp.com/s/xxxx\n"
        "• mirrobox.com/s/xxxx\n"
        "• dan mirror lainnya\n\n"
        "Ketik /help untuk bantuan."
    )

    if config.VIP_ENABLED:
        if not db.is_vip(user.id):
            trial_info = ""
            if config.VIP_TRIAL_ENABLED:
                trial_info = f"\n🎁 Free trial: {config.VIP_TRIAL_DOWNLOADS}x download!"
            text += f"\n\n💎 Butuh VIP untuk download.{trial_info}\nKetik /vip untuk info."

    await update.message.reply_text(text, parse_mode="HTML")


async def help_command(update: Update, context):
    """Handle /help."""
    text = (
        "📖 <b>Bantuan Terabox Downloader</b>\n\n"
        "1️⃣ Kirim link Terabox\n"
        "2️⃣ Bot akan resolve & download\n"
        "3️⃣ File dikirim ke kamu\n\n"
        "<b>Perintah:</b>\n"
        "/start — Mulai bot\n"
        "/help — Bantuan ini\n"
        "/vip — Info langganan VIP\n"
        "/status — Cek status VIP\n"
        "/bayar — Beli VIP\n"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def vip_command(update: Update, context):
    """Handle /vip — show VIP info."""
    if not config.VIP_ENABLED:
        await update.message.reply_text("VIP tidak diaktifkan. Semua download gratis!")
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

    text = format_vip_info()
    await update.message.reply_text(text, parse_mode="HTML")


async def status_command(update: Update, context):
    """Handle /status — check VIP status."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if not user:
        await update.message.reply_text("Ketik /start dulu ya.")
        return

    vip_status = "✅ VIP" if db.is_vip(user_id) else "❌ Free"
    remaining = db.get_remaining_days(user_id)
    dur = "Lifetime" if remaining is None else f"{remaining} hari"

    text = (
        f"📊 <b>Status Akun</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"💎 Status: {vip_status}\n"
        f"📥 Total Download: {user.get('total_downloads', 0)}\n"
    )
    if db.is_vip(user_id):
        text += f"⏳ Sisa: {dur}\n"

    if config.VIP_TRIAL_ENABLED and not db.is_vip(user_id):
        used = db.get_free_downloads_used(user_id)
        text += f"🎁 Trial dipakai: {used}/{config.VIP_TRIAL_DOWNLOADS}\n"

    await update.message.reply_text(text, parse_mode="HTML")


# ── PAYMENT FLOW ─────────────────────────────────────

async def bayar_start(update: Update, context):
    """Handle /bayar — start payment flow."""
    if not config.VIP_ENABLED:
        await update.message.reply_text("VIP tidak diaktifkan.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    if db.is_vip(user_id):
        await update.message.reply_text("Kamu sudah VIP! Tidak perlu bayar lagi.")
        return ConversationHandler.END

    await update.message.reply_text(
        f"💳 <b>Pembayaran VIP</b>\n\n"
        f"💰 Nominal: <b>Rp {config.VIP_PRICE:,}</b>\n\n"
        f"📲 Silakan transfer ke rekening admin,\n"
        f"   lalu kirim bukti screenshot di sini.\n\n"
        f"Ketik /cancel untuk batal.",
        parse_mode="HTML",
    )
    return AWAIT_PROOF


async def bayar_receive_proof(update: Update, context):
    """Receive payment proof."""
    user_id = update.effective_user.id

    if not update.message.photo:
        await update.message.reply_text(
            "Kirim bukti transfer berupa foto/screenshot.\n"
            "Ketik /cancel untuk batal."
        )
        return AWAIT_PROOF

    # Get largest photo
    photo = update.message.photo[-1]

    payment_id = await handle_payment(
        bot=context.bot,
        user_id=user_id,
        amount=config.VIP_PRICE,
        method=config.PAYMENT_METHOD,
        proof_file_id=photo.file_id,
    )

    await update.message.reply_text(
        "✅ <b>Bukti diterima!</b>\n\n"
        f"🆔 ID Pembayaran: <code>{payment_id}</code>\n"
        "⏳ Menunggu verifikasi admin...\n\n"
        "Kamu akan dapat notifikasi setelah dikonfirmasi.",
        parse_mode="HTML",
    )
    return ConversationHandler.END


async def bayar_cancel(update: Update, context):
    """Cancel payment flow."""
    await update.message.reply_text("❌ Pembayaran dibatalkan.")
    return ConversationHandler.END


# ── MAIN LINK HANDLER ────────────────────────────────

async def handle_link(update: Update, context):
    """Process Terabox link from user message."""
    user_id = update.effective_user.id
    text = update.message.text

    # Check if message contains terabox link
    url = extract_urls(text)
    if not url:
        return  # Not a terabox link, ignore

    # Register user if new
    db.create_user(user_id, update.effective_user.username, update.effective_user.full_name)

    # ── VIP CHECK ──
    if config.VIP_ENABLED and not db.is_vip(user_id):
        if config.VIP_TRIAL_ENABLED:
            used = db.get_free_downloads_used(user_id)
            if used >= config.VIP_TRIAL_DOWNLOADS:
                await update.message.reply_text(
                    "⛔ <b>Trial habis!</b>\n\n"
                    f"Kamu sudah pakai {used}/{config.VIP_TRIAL_DOWNLOADS} download gratis.\n"
                    "Ketik /vip untuk beli akses.",
                    parse_mode="HTML",
                )
                return
        else:
            await update.message.reply_text(
                "⛔ <b>VIP Required</b>\n\n"
                "Ketik /vip untuk info langganan.",
                parse_mode="HTML",
            )
            return

    # ── PROCESS ──
    status_msg = await update.message.reply_text("🔍 Memproses link...")

    result = await resolve_terabox(url)

    if not result["success"]:
        await status_msg.edit_text(
            f"❌ <b>Gagal resolve link</b>\n\n{result.get('error', 'Unknown error')}\n\n"
            "Coba lagi nanti atau cek apakah link valid.",
            parse_mode="HTML",
        )
        return

    # Build info message
    file_name = result["file_name"] or "Unknown"
    file_size = result["size"] or "Unknown"
    icon = get_file_icon(os.path.splitext(file_name)[1]) if file_name else "📁"
    sizebytes = result.get("sizebytes", 0)

    info_text = (
        f"{icon} <b>{file_name}</b>\n"
        f"📦 <b>{file_size}</b>\n"
        f"🔗 Strategi: {result['strategy_used']}"
    )

    await status_msg.edit_text(info_text, parse_mode="HTML")

    # Check if file is too large for Telegram
    max_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024

    if sizebytes and sizebytes > max_bytes:
        # File too large — send direct link
        await update.message.reply_text(
            f"⚠️ File terlalu besar untuk dikirim via Telegram (>{config.MAX_FILE_SIZE_MB} MB).\n\n"
            f"🔗 <b>Direct Link:</b>\n"
            f"<a href='{result['direct_link']}'>Klik di sini untuk download</a>\n\n"
            f"⏰ Link berlaku terbatas. Download sekarang!",
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
        db.add_download_count(user_id)
        return

    # Download + Upload for small files
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

def main():
    """Start the bot."""
    # Validate config
    missing = config.validate()
    if missing:
        logger.error(f"Missing config: {', '.join(missing)}")
        return

    # Initialize database
    migrate(config.db_path())
    db.init()

    # Build application
    app = Application.builder().token(config.BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("vip", vip_command))
    app.add_handler(CommandHandler("status", status_command))

    # Payment conversation
    payment_conv = ConversationHandler(
        entry_points=[CommandHandler("bayar", bayar_start)],
        states={
            AWAIT_PROOF: [
                MessageHandler(filters.PHOTO, bayar_receive_proof),
                MessageHandler(filters.TEXT & ~filters.COMMAND, bayar_start),
            ],
        },
        fallbacks=[CommandHandler("cancel", bayar_cancel)],
    )
    app.add_handler(payment_conv)

    # Admin commands
    app.add_handler(CommandHandler("pending", pending_command))
    app.add_handler(CommandHandler("approve", approve_command))
    app.add_handler(CommandHandler("reject", reject_command))
    app.add_handler(CommandHandler("vipadd", vipadd_command))
    app.add_handler(CommandHandler("viprem", viprem_command))
    app.add_handler(CommandHandler("vips", vips_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("config", config_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    # Inline callbacks
    app.add_handler(CallbackQueryHandler(approve_callback, pattern=r"^appr_\d+"))
    app.add_handler(CallbackQueryHandler(reject_callback, pattern=r"^rej_\d+"))

    # Link handler — matches text containing terabox URLs
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_link,
    ))

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import os  # noqa: for os.path usage in handle_link
    main()
