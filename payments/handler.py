"""Payment handler — KlikQRIS dynamic QR integration."""

import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config
from database.models import db
from payments.klikqris import create_transaction, check_status, generate_order_id

logger = logging.getLogger(__name__)


def vip_info_text() -> str:
    """Formatted VIP information."""
    dur = (
        "Lifetime ♾️"
        if config.VIP_DURATION_DAYS == 0
        else f"{config.VIP_DURATION_DAYS} hari"
    )
    return (
        f"⭐ <b>VIP Terabox Downloader</b>\n\n"
        f"💰 Harga: <b>Rp {config.VIP_PRICE:,}</b>\n"
        f"⏳ Durasi: <b>{dur}</b>\n"
        f"📥 Benefit: Unlimited download, no ads\n\n"
        "👇 Klik tombol di bawah untuk mulai pembayaran via QRIS:"
    )


async def bayar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bayar — initiate KlikQRIS payment."""
    user = update.effective_user
    telegram_id = user.id

    # Check if user already VIP
    if db.is_vip(telegram_id):
        remaining = db.get_remaining_days(telegram_id)
        if remaining is None:
            await update.message.reply_text(
                "🎉 Kamu sudah VIP Lifetime! Kirim link Terabox untuk download."
            )
        else:
            await update.message.reply_text(
                f"✅ Kamu sudah VIP!\n⏳ Sisa: {remaining} hari lagi."
            )
        return

    # Check if user has pending payment
    pending = db.get_user_pending_payment(telegram_id)
    if pending:
        order_id = pending["order_id"]
        # Check expired or still valid
        status_result = await check_status(order_id)
        if status_result.get("success"):
            k_status = status_result["status"]
            if k_status == "SUCCESS":
                db.approve_payment_by_order_id(order_id)
                db.set_vip(telegram_id, config.VIP_DURATION_DAYS)
                dur = (
                    "Lifetime ♾️"
                    if config.VIP_DURATION_DAYS == 0
                    else f"{config.VIP_DURATION_DAYS} hari"
                )
                await update.message.reply_text(
                    f"✅ Pembayaran sebelumnya terdeteksi!\n🎉 VIP aktif selama {dur}."
                )
                return
            elif k_status == "EXPIRED":
                # Remove expired payment
                pass  # Will create new one below
            else:
                # Still PENDING — re-send QR
                await update.message.reply_text(
                    "⏳ Kamu masih punya pembayaran pending. Silakan scan QR di bawah:"
                )
                if status_result.get("raw", {}).get("qris_url"):
                    await update.message.reply_photo(
                        photo=status_result["raw"]["qris_url"],
                        caption=(
                            f"💳 <b>QRIS — Bayar Sebelum Expired</b>\n\n"
                            f"🆔 {order_id}\n"
                            f"💰 Rp {int(status_result['total_amount']):,}\n"
                            f"⏰ Expired: {status_result.get('expired_at', 'N/A')}\n\n"
                            "📱 Scan pakai GoPay/OVO/DANA/M-Banking"
                        ),
                        parse_mode="HTML",
                    )
                return

    # Show VIP info
    await update.message.reply_text(
        vip_info_text(),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Bayar via QRIS", callback_data="pay_qris")],
            [InlineKeyboardButton("ℹ️ Cek Status", callback_data="pay_status")],
        ]),
    )


async def pay_qris_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Bayar via QRIS' button — create KlikQRIS transaction."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id

    # Validate config
    if not config.VIP_ENABLED:
        await query.edit_message_text("⛔ VIP mode belum diaktifkan.")
        return

    if not config.KLIKQRIS_API_KEY or not config.KLIKQRIS_MERCHANT_ID:
        await query.edit_message_text(
            "⚠️ Payment gateway belum dikonfigurasi.\nHubungi admin untuk setup KlikQRIS."
        )
        return

    # Create KlikQRIS transaction
    order_id = generate_order_id(telegram_id)

    await query.edit_message_text("⏳ Membuat QR Code pembayaran...")

    result = await create_transaction(
        order_id=order_id,
        amount=config.VIP_PRICE,
        keterangan=f"VIP Terabox {config.VIP_DURATION_DAYS}h — {user.id}",
    )

    if not result.get("success"):
        await query.edit_message_text(
            f"❌ Gagal membuat pembayaran.\nError: {result.get('error', 'Unknown')}\n\nCoba lagi nanti atau hubungi admin."
        )
        return

    # Save payment to DB
    db.create_payment(
        telegram_id=telegram_id,
        amount=config.VIP_PRICE,
        method="klikqris",
        order_id=order_id,
        signature=result.get("signature", ""),
    )

    # Send QR code
    dur = (
        "Lifetime ♾️"
        if config.VIP_DURATION_DAYS == 0
        else f"{config.VIP_DURATION_DAYS} hari"
    )

    qr_url = result.get("qris_url", "")
    total_amount = result.get("total_amount", config.VIP_PRICE)
    expired = result.get("expired_at", "")

    if qr_url:
        await query.delete_message()
        await query.message.reply_photo(
            photo=qr_url,
            caption=(
                f"💳 <b>QRIS Pembayaran VIP</b>\n\n"
                f"🆔 <code>{order_id}</code>\n"
                f"💰 Rp {int(total_amount):,}\n"
                f"⏳ Durasi: {dur}\n"
                f"⏰ Expired: {expired}\n\n"
                "📱 Scan pakai GoPay / OVO / DANA / M-Banking\n"
                "✅ VIP otomatis aktif setelah pembayaran sukses!"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Cek Status", callback_data=f"checkpay_{order_id}")],
                [InlineKeyboardButton("🆘 Bantuan", callback_data="help")],
            ]),
        )
    else:
        # Fallback: no QR URL (e.g., MY PG mode)
        await query.edit_message_text(
            f"✅ Transaksi dibuat!\n\n🆔 <code>{order_id}</code>\n💰 Rp {int(total_amount):,}\n⏰ Expired: {expired}\n\n"
            "Silakan lanjutkan pembayaran. Gunakan /status untuk cek.",
            parse_mode="HTML",
        )


async def pay_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Cek Status' button — check pending payment."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    telegram_id = user.id

    # Parse order_id from callback data if present
    data = query.data
    order_id = None
    if data.startswith("checkpay_"):
        order_id = data.replace("checkpay_", "")

    if not order_id:
        pending = db.get_user_pending_payment(telegram_id)
        if not pending:
            await query.edit_message_text(
                "Tidak ada pembayaran pending.\nGunakan /bayar untuk mulai.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Bayar Sekarang", callback_data="pay_qris")],
                ]),
            )
            return
        order_id = pending["order_id"]

    result = await check_status(order_id)

    if not result.get("success"):
        await query.edit_message_text(f"❌ Gagal cek status: {result.get('error')}")
        return

    status = result["status"]
    dur = (
        "Lifetime ♾️"
        if config.VIP_DURATION_DAYS == 0
        else f"{config.VIP_DURATION_DAYS} hari"
    )

    if status == "SUCCESS":
        db.approve_payment_by_order_id(order_id)
        db.set_vip(telegram_id, config.VIP_DURATION_DAYS)
        await query.edit_message_text(
            f"✅ <b>Pembayaran Berhasil!</b>\n\n🎉 VIP kamu sudah aktif selama {dur}.\nKirim link Terabox sekarang!",
            parse_mode="HTML",
        )
    elif status == "EXPIRED":
        await query.edit_message_text(
            "⏰ QR Code sudah expired.\nSilakan buat pembayaran baru.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Buat Baru", callback_data="pay_qris")],
            ]),
        )
    else:  # PENDING
        await query.edit_message_text(
            f"⏳ Status: <b>Menunggu Pembayaran</b>\n\n"
            f"🆔 <code>{order_id}</code>\n"
            f"💰 Rp {int(result.get('total_amount', 0)):,}\n\n"
            "Silakan scan QR dan selesaikan pembayaran.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Cek Lagi", callback_data=f"checkpay_{order_id}")],
            ]),
        )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status — show user VIP + payment status."""
    user = update.effective_user

    # Ensure user exists
    db.create_user(user.id, user.username, user.full_name)

    lines = [f"📊 <b>Status — {user.full_name or user.username}</b>\n"]

    if db.is_vip(user.id):
        remaining = db.get_remaining_days(user.id)
        if remaining is None:
            lines.append("⭐ VIP: <b>Lifetime</b> ♾️")
        else:
            lines.append(f"⭐ VIP: <b>Aktif</b> ({remaining} hari tersisa)")
    else:
        lines.append("👤 Status: <b>Free</b>")

    downloads = db.get_free_downloads_used(user.id)
    lines.append(f"📥 Total Download: {downloads}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")
