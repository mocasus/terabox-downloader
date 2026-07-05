"""Terabox Downloader Bot — Main entry point.

Runs two services concurrently:
- Telegram bot (polling) — handles all user/admin commands + inline callbacks
- KlikQRIS webhook server — receives payment callbacks on config.WEBHOOK_PORT

Architecture:
    User Message → MessageHandler → URL extraction → VIP check → Resolver
    → Downloader → Upload to Telegram → Done

    /bayar → KlikQRIS API → QR Code → User pays → Webhook → Auto VIP
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import config
from database.models import db
from database.migrations import migrate
from terabox.downloader import download_file, upload_to_telegram
from terabox.resolver import resolve as resolve_terabox
from terabox.utils import extract_urls, get_file_icon, format_size
from payments.handler import (
    bayar_command,
    pay_qris_callback,
    pay_status_callback,
    status_command as pay_status_command,
    vip_info_text,
)
from payments.webhook_server import start_webhook_server
from admin.handlers import (
    approve_callback,
    approve_command,
    broadcast_command,
    config_command,
    pending_command,
    reject_callback,
    reject_command,
    stats_command,
    vipadd_command,
    viprem_command,
    vips_command,
)

# ── Constants ──────────────────────────────────────

logger = logging.getLogger(__name__)

# Inline keyboard templates
KB_START = InlineKeyboardMarkup([
    [InlineKeyboardButton("💰 Beli VIP", callback_data="pay_qris"),
     InlineKeyboardButton("⬇️ Download", callback_data="help_download")],
    [InlineKeyboardButton("ℹ️ Bantuan", callback_data="help_main"),
     InlineKeyboardButton("👤 Status", callback_data="pay_status")],
])

KB_HELP = InlineKeyboardMarkup([
    [InlineKeyboardButton("💳 Cara Bayar", callback_data="help_bayar"),
     InlineKeyboardButton("⭐ Info VIP", callback_data="help_vip")],
    [InlineKeyboardButton("📊 Cek Status", callback_data="pay_status"),
     InlineKeyboardButton("🆘 FAQ", callback_data="help_faq")],
])

KB_AFTER_DOWNLOAD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Download Lagi", callback_data="help_download"),
     InlineKeyboardButton("⭐ Beli VIP", callback_data="pay_qris")],
    [InlineKeyboardButton("📊 Status", callback_data="pay_status")],
])

KB_AFTER_DOWNLOAD_VIP = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Download Lagi", callback_data="help_download"),
     InlineKeyboardButton("📊 Status", callback_data="pay_status")],
])

KB_AFTER_ERROR = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Coba Lagi", callback_data="help_download"),
     InlineKeyboardButton("🆘 Bantuan", callback_data="help_main")],
])

KB_TRIAL_HABIS = InlineKeyboardMarkup([
    [InlineKeyboardButton("💳 Beli VIP Sekarang", callback_data="pay_qris")],
    [InlineKeyboardButton("ℹ️ Info VIP", callback_data="help_vip")],
])

KB_VIP_REQUIRED = InlineKeyboardMarkup([
    [InlineKeyboardButton("💳 Beli VIP", callback_data="pay_qris")],
    [InlineKeyboardButton("ℹ️ Info VIP", callback_data="help_vip")],
])

KB_AFTER_BAYAR_SUCCESS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Cek Status", callback_data="pay_status"),
     InlineKeyboardButton("⬇️ Mulai Download", callback_data="help_download")],
])

KB_STATUS_FREE = InlineKeyboardMarkup([
    [InlineKeyboardButton("💳 Beli VIP", callback_data="pay_qris")],
])

KB_STATUS_VIP = InlineKeyboardMarkup([
    [InlineKeyboardButton("📊 Info VIP", callback_data="help_vip")],
])


# ── User Commands ───────────────────────────────────

async def start(update: Update, context) -> None:
    """Handle /start — welcome message + inline menu.

    Registers user in database on first interaction.
    """
    user = update.effective_user
    db.create_user(user.id, user.username, user.full_name)

    text = (
        f"👋 Halo <b>{user.first_name}</b>!\n\n"
        "🚀 <b>Terabox Downloader Bot</b>\n"
        "Kirim link Terabox, aku download-in langsung ke chat kamu!\n\n"
        "🔗 <b>Link yang didukung:</b>\n"
        "• <code>terabox.com/s/xxxx</code>\n"
        "• <code>teraboxapp.com/s/xxxx</code>\n"
        "• <code>mirrobox.com/s/xxxx</code>\n"
        "• <code>1024tera.com/s/xxxx</code>\n"
        "• dan mirror lainnya\n\n"
        "👇 <b>Pilih menu di bawah:</b>"
    )

    if config.VIP_ENABLED and not db.is_vip(user.id):
        trial_info = ""
        if config.VIP_TRIAL_ENABLED:
            trial_info = (
                f"\n🎁 <b>Free Trial:</b> {config.VIP_TRIAL_DOWNLOADS}x download gratis!"
            )
        text += trial_info

    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=KB_START,
    )


async def help_command(update: Update, context) -> None:
    """Handle /help — show help with inline navigation."""
    text = (
        "📖 <b>Bantuan Terabox Downloader</b>\n\n"
        "<b>🔗 Cara Download:</b>\n"
        "1️⃣ Kirim link Terabox ke chat ini\n"
        "2️⃣ Bot akan resolve & download otomatis\n"
        "3️⃣ File langsung dikirim ke kamu\n\n"
        "<b>💳 Cara Bayar VIP:</b>\n"
        "1️⃣ Klik /bayar atau tombol di bawah\n"
        "2️⃣ Scan QR code dengan e-wallet\n"
        "3️⃣ VIP otomatis aktif setelah bayar!\n\n"
        "👇 <b>Pilih bantuan lebih lanjut:</b>"
    )
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=KB_HELP,
    )


async def vip_command(update: Update, context) -> None:
    """Handle /vip — show VIP info with pay button."""
    if not config.VIP_ENABLED:
        await update.message.reply_text(
            "🎉 VIP tidak diaktifkan. Semua download gratis!",
        )
        return

    user_id = update.effective_user.id
    if db.is_vip(user_id):
        remaining = db.get_remaining_days(user_id)
        dur = "Lifetime ♾️" if remaining is None else f"{remaining} hari lagi"
        await update.message.reply_text(
            f"💎 Kamu sudah <b>VIP</b>!\n⏳ Masa aktif: <b>{dur}</b>\n\n"
            "Kirim link Terabox untuk download.",
            parse_mode="HTML",
            reply_markup=KB_STATUS_VIP,
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


# ── Inline Help Callbacks ────────────────────────────

async def help_download_callback(update: Update, context) -> None:
    """Show how to download with inline buttons."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔗 <b>Cara Download File Terabox</b>\n\n"
        "1️⃣ Copy link Terabox yang ingin didownload\n"
        "2️⃣ Paste / kirim link ke chat ini\n"
        "3️⃣ Bot akan otomatis memproses\n"
        "4️⃣ File dikirim langsung ke kamu!\n\n"
        "<b>Contoh link:</b>\n"
        "<code>https://terabox.com/s/1abc2def3456</code>\n\n"
        "⚠️ Pastikan link bisa diakses (tidak private).\n"
        "📦 Max file size: 50MB (lebih besar dikirim direct link).",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="help_main")],
        ]),
    )


async def help_main_callback(update: Update, context) -> None:
    """Show main help menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 <b>Menu Bantuan</b>\n\nPilih topik:",
        parse_mode="HTML",
        reply_markup=KB_HELP,
    )


async def help_bayar_callback(update: Update, context) -> None:
    """Show payment help."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💳 <b>Cara Pembayaran VIP</b>\n\n"
        "1️⃣ Klik <b>Bayar via QRIS</b>\n"
        "2️⃣ QR code akan muncul\n"
        "3️⃣ Scan pakai:\n"
        "   • GoPay\n"
        "   • OVO\n"
        "   • DANA\n"
        "   • M-Banking (BCA, Mandiri, BRI, BNI)\n"
        "   • ShopeePay\n"
        "4️⃣ Setelah bayar, VIP otomatis aktif!\n\n"
        "⏰ QR code berlaku 15 menit.\n"
        "🔄 Kalau expired, buat baru aja.\n\n"
        "❓ Masalah? Klik 🆘 FAQ atau hubungi admin.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Bayar Sekarang", callback_data="pay_qris")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="help_main")],
        ]),
    )


async def help_vip_callback(update: Update, context) -> None:
    """Show VIP info."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        vip_info_text(),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Bayar via QRIS", callback_data="pay_qris")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="help_main")],
        ]),
    )


async def help_faq_callback(update: Update, context) -> None:
    """Show FAQ."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🆘 <b>FAQ — Pertanyaan Umum</b>\n\n"
        "<b>Q: File ga kekirim?</b>\n"
        "A: Cek apakah link valid & tidak private.\n"
        "   File >50MB dikirim sebagai direct link.\n\n"
        "<b>Q: Bayar tapi VIP belum aktif?</b>\n"
        "A: Tunggu 1-2 menit. Kalau lebih, klik Cek Status.\n"
        "   Atau hubungi admin.\n\n"
        "<b>Q: QR code expired?</b>\n"
        "A: QR berlaku 15 menit. Buat baru aja, gratis.\n\n"
        "<b>Q: Trial habis, gimana?</b>\n"
        "A: Beli VIP — sekali bayar, download sepuasnya!\n\n"
        "<b>Q: Bot error / ga respon?</b>\n"
        "A: Coba /start lagi. Kalau masih, hubungi admin.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Hubungi Admin", url="https://t.me/rubuskap")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="help_main")],
        ]),
    )


# ── Main Link Handler ────────────────────────────────

async def handle_link(update: Update, context) -> None:
    """Process Terabox link from user message.

    Flow:
        1. Extract URL
        2. VIP check
        3. Resolve link
        4. Download file
        5. Upload to Telegram
    """
    user_id: int = update.effective_user.id
    text: str = update.message.text

    # Extract Terabox URL
    url: Optional[str] = extract_urls(text)
    if not url:
        return  # Not a Terabox link

    # Register user
    db.create_user(
        user_id,
        update.effective_user.username,
        update.effective_user.full_name,
    )

    # ── VIP Gate ──
    if config.VIP_ENABLED and not db.is_vip(user_id):
        if config.VIP_TRIAL_ENABLED:
            used = db.get_free_downloads_used(user_id)
            if used >= config.VIP_TRIAL_DOWNLOADS:
                await update.message.reply_text(
                    f"⛔ <b>Trial Habis!</b>\n\n"
                    f"Kamu sudah pakai <b>{used}/{config.VIP_TRIAL_DOWNLOADS}</b> "
                    f"download gratis.\n"
                    "Beli VIP untuk download unlimited! 👇",
                    parse_mode="HTML",
                    reply_markup=KB_TRIAL_HABIS,
                )
                return
        else:
            await update.message.reply_text(
                "⛔ <b>VIP Required</b>\n\n"
                "Kamu perlu VIP untuk download.\n"
                "Klik tombol di bawah untuk beli 👇",
                parse_mode="HTML",
                reply_markup=KB_VIP_REQUIRED,
            )
            return

    # ── Resolve ──
    status_msg = await update.message.reply_text("🔍 Memproses link...")
    result = await resolve_terabox(url)

    if not result["success"]:
        await status_msg.edit_text(
            f"❌ <b>Gagal resolve link</b>\n\n"
            f"{result.get('error', 'Unknown error')}\n\n"
            "Coba lagi nanti atau cek apakah link valid.",
            parse_mode="HTML",
            reply_markup=KB_AFTER_ERROR,
        )
        return

    # Build file info
    file_name: str = result["file_name"] or "Unknown"
    ext: str = os.path.splitext(file_name)[1] if file_name else ""
    icon: str = get_file_icon(ext)
    sizebytes: int = result.get("sizebytes", 0)
    file_size: str = result.get("size", "Unknown")

    await status_msg.edit_text(
        f"{icon} <b>{file_name}</b>\n"
        f"📦 <b>{file_size}</b>\n"
        f"🔗 Strategi: <code>{result['strategy_used']}</code>",
        parse_mode="HTML",
    )

    # Check max file size
    max_bytes: int = config.MAX_FILE_SIZE_MB * 1024 * 1024

    if sizebytes and sizebytes > max_bytes:
        await update.message.reply_text(
            f"⚠️ File terlalu besar untuk Telegram "
            f"(>{config.MAX_FILE_SIZE_MB} MB).\n\n"
            f"🔗 <b>Download langsung:</b>\n"
            f"<a href='{result['direct_link']}'>Klik di sini</a>\n\n"
            "⏰ Link berlaku terbatas. Download sekarang!",
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
        db.add_download_count(user_id)
        await status_msg.delete()
        return

    # ── Download + Upload ──
    progress_msg = await update.message.reply_text("⬇️ Mendownload...")

    async def dl_progress(downloaded: int, total: int) -> None:
        pct = int(downloaded / total * 100) if total else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        try:
            await progress_msg.edit_text(
                f"⬇️ Mendownload... {pct}%\n[{bar}]"
            )
        except Exception:
            pass

    file_path = await download_file(
        result["direct_link"],
        file_name,
        progress_callback=dl_progress if sizebytes else None,
    )

    if not file_path:
        await progress_msg.edit_text(
            "❌ Gagal mendownload file. Coba lagi nanti.",
            reply_markup=KB_AFTER_ERROR,
        )
        return

    await progress_msg.edit_text("📤 Mengupload ke Telegram...")

    caption = f"{icon} <b>{file_name}</b>\n📦 {file_size}"
    success = await upload_to_telegram(
        context.bot, user_id, file_path, file_name,
        file_size=sizebytes, caption=caption,
    )

    if success:
        await progress_msg.delete()
        db.add_download_count(user_id)

        # Choose keyboard: VIP users don't need "Beli VIP" button
        kb = KB_AFTER_DOWNLOAD_VIP if db.is_vip(user_id) else KB_AFTER_DOWNLOAD
        await update.message.reply_text(
            f"✅ <b>Download Selesai!</b>\n\n"
            f"{icon} {file_name}\n"
            f"📦 {file_size}\n\n"
            "Mau download file lain? Kirim link lagi! 👇",
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await progress_msg.edit_text(
            f"⚠️ Upload gagal (file mungkin terlalu besar).\n\n"
            f"🔗 <b>Download langsung:</b>\n"
            f"<a href='{result['direct_link']}'>Klik di sini</a>",
            parse_mode="HTML",
            reply_markup=KB_AFTER_ERROR,
        )


# ── Main ─────────────────────────────────────────────

async def main() -> None:
    """Start bot polling + webhook server."""
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

    # Build Telegram application
    app = Application.builder().token(config.BOT_TOKEN).build()

    # ── User Commands ──
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("vip", vip_command))
    app.add_handler(CommandHandler("bayar", bayar_command))
    app.add_handler(CommandHandler("status", pay_status_command))

    # ── Admin Commands ──
    app.add_handler(CommandHandler("pending", pending_command))
    app.add_handler(CommandHandler("approve", approve_command))
    app.add_handler(CommandHandler("reject", reject_command))
    app.add_handler(CommandHandler("vipadd", vipadd_command))
    app.add_handler(CommandHandler("viprem", viprem_command))
    app.add_handler(CommandHandler("vips", vips_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("config", config_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    # ── Payment Callbacks ──
    app.add_handler(CallbackQueryHandler(pay_qris_callback, pattern="^pay_qris$"))
    app.add_handler(CallbackQueryHandler(pay_status_callback, pattern=r"^pay_status$|^checkpay_"))

    # ── Help Callbacks ──
    app.add_handler(CallbackQueryHandler(help_download_callback, pattern="^help_download$"))
    app.add_handler(CallbackQueryHandler(help_main_callback, pattern="^help_main$"))
    app.add_handler(CallbackQueryHandler(help_bayar_callback, pattern="^help_bayar$"))
    app.add_handler(CallbackQueryHandler(help_vip_callback, pattern="^help_vip$"))
    app.add_handler(CallbackQueryHandler(help_faq_callback, pattern="^help_faq$"))

    # ── Admin Callbacks ──
    app.add_handler(CallbackQueryHandler(approve_callback, pattern=r"^appr_\d+"))
    app.add_handler(CallbackQueryHandler(reject_callback, pattern=r"^rej_\d+"))

    # ── Link Handler (last priority) ──
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
        # Keep running indefinitely
        await asyncio.Event().wait()
    finally:
        await app.stop()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
