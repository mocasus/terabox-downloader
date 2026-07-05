"""Admin command handlers."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import config
from database.models import db

logger = logging.getLogger(__name__)

__all__ = [
    "is_admin",
    "pending_command",
    "approve_callback",
    "reject_callback",
    "vipadd_command",
    "viprem_command",
    "vips_command",
    "stats_command",
    "config_command",
    "approve_command",
    "reject_command",
]


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


async def pending_command(update, context):
    """Show pending payments with inline keyboard."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    payments = db.get_pending_payments()
    if not payments:
        await update.message.reply_text("✅ Tidak ada pembayaran pending.")
        return

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    for p in payments:
        text = (
            f"💳 <b>Pembayaran #{p['id']}</b>\n"
            f"👤 User: <code>{p['telegram_id']}</code>\n"
            f"💰 Rp {p['amount']:,}\n"
            f"📲 {p['method']}\n"
            f"📅 {p['created_at']}"
        )
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"appr_{p['id']}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rej_{p['id']}"),
            ]
        ])

        if p.get("proof_file"):
            await update.message.reply_photo(
                photo=p["proof_file"],
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode="HTML",
                reply_markup=kb,
            )


async def approve_callback(update, context):
    """Handle approve button."""
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    payment_id = int(query.data.split("_")[1])
    payment = db.get_payment(payment_id)

    if not payment or payment["status"] != "pending":
        await query.edit_message_caption(caption=f"⏳ Pembayaran #{payment_id} sudah diproses.")
        return

    db.approve_payment(payment_id)
    db.set_vip(payment["telegram_id"], config.VIP_DURATION_DAYS)

    dur = "Lifetime" if config.VIP_DURATION_DAYS == 0 else f"{config.VIP_DURATION_DAYS} hari"
    await query.edit_message_caption(
        caption=f"✅ Pembayaran #{payment_id} <b>DISETUJUI</b>\nVIP {dur} untuk user {payment['telegram_id']}",
        parse_mode="HTML",
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=payment["telegram_id"],
            text=(
                f"🎉 <b>Pembayaran Dikonfirmasi!</b>\n\n"
                f"VIP kamu sudah aktif!\n"
                f"⏳ Masa aktif: {dur}\n\n"
                f"Silakan kirim link Terabox untuk di-download."
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass


async def reject_callback(update, context):
    """Handle reject button — just mark as rejected, admin types reason later."""
    query = update.callback_query

    if not is_admin(query.from_user.id):
        await query.answer("⛔ Admin only.")
        return

    payment_id = int(query.data.split("_")[1])
    payment = db.get_payment(payment_id)

    if not payment or payment["status"] != "pending":
        await query.answer("Sudah diproses.")
        return

    db.reject_payment(payment_id, "Ditolak admin")
    await query.edit_message_caption(
        caption=f"❌ Pembayaran #{payment_id} <b>DITOLAK</b>",
        parse_mode="HTML",
    )

    try:
        await context.bot.send_message(
            chat_id=payment["telegram_id"],
            text="❌ <b>Pembayaran Ditolak</b>\n\nSilakan hubungi admin untuk info lebih lanjut.",
            parse_mode="HTML",
        )
    except Exception:
        pass


async def vipadd_command(update, context):
    """Manual add VIP: /vipadd <user_id> <days>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Usage: /vipadd <user_id> <days>\nDays=0 untuk lifetime.")
        return

    try:
        user_id = int(args[0])
        days = int(args[1]) if len(args) > 1 else config.VIP_DURATION_DAYS
    except ValueError:
        await update.message.reply_text("ID dan hari harus angka.")
        return

    db.create_user(user_id)
    db.set_vip(user_id, days)

    dur = "Lifetime" if days == 0 else f"{days} hari"
    await update.message.reply_text(f"✅ VIP {dur} diberikan ke user {user_id}")


async def viprem_command(update, context):
    """Remove VIP: /viprem <user_id>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /viprem <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID harus angka.")
        return

    db.remove_vip(user_id)
    await update.message.reply_text(f"✅ VIP user {user_id} dicabut.")


async def vips_command(update, context):
    """List all VIP users."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    users = db.get_all_vip_users()
    if not users:
        await update.message.reply_text("Belum ada user VIP.")
        return

    lines = ["👑 <b>VIP Users:</b>\n"]
    for u in users:
        expiry = u.get("vip_expiry") or "Lifetime"
        lines.append(
            f"• <code>{u['telegram_id']}</code> — {u.get('username') or 'N/A'} — Exp: {expiry}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def stats_command(update, context):
    """Show bot statistics."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    s = db.get_stats()
    text = (
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: {s['total_users']}\n"
        f"👑 VIP Users: {s['vip_users']}\n"
        f"🆕 New Today: {s['new_today']}\n"
        f"⏳ Pending Payments: {s['pending_payments']}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def config_command(update, context):
    """Show current bot configuration."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    dur = "Lifetime" if config.VIP_DURATION_DAYS == 0 else f"{config.VIP_DURATION_DAYS} hari"
    text = (
        f"⚙️ <b>Current Config</b>\n\n"
        f"VIP Enabled: {config.VIP_ENABLED}\n"
        f"VIP Price: Rp {config.VIP_PRICE:,}\n"
        f"VIP Duration: {dur}\n"
        f"Trial Enabled: {config.VIP_TRIAL_ENABLED}\n"
        f"Trial Downloads: {config.VIP_TRIAL_DOWNLOADS}\n"
        f"Payment Method: {config.PAYMENT_METHOD}\n"
        f"Max File Size: {config.MAX_FILE_SIZE_MB} MB\n"
        f"Concurrent DL: {config.CONCURRENT_DOWNLOADS}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def approve_command(update, context):
    """Handle /approve <payment_id>."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /approve <payment_id>")
        return
    try:
        pid = int(args[0])
    except ValueError:
        await update.message.reply_text("ID harus angka.")
        return

    payment = db.get_payment(pid)
    if not payment or payment["status"] != "pending":
        await update.message.reply_text(f"Pembayaran #{pid} tidak ditemukan atau sudah diproses.")
        return

    db.approve_payment(pid)
    db.set_vip(payment["telegram_id"], config.VIP_DURATION_DAYS)
    dur = "Lifetime" if config.VIP_DURATION_DAYS == 0 else f"{config.VIP_DURATION_DAYS} hari"
    await update.message.reply_text(f"✅ #{pid} disetujui — VIP {dur} untuk {payment['telegram_id']}")

    try:
        await context.bot.send_message(
            chat_id=payment["telegram_id"],
            text=f"🎉 <b>Pembayaran Dikonfirmasi!</b>\n\nVIP kamu sudah aktif!\n⏳ Masa aktif: {dur}",
            parse_mode="HTML",
        )
    except Exception:
        pass


async def reject_command(update, context):
    """Handle /reject <payment_id> <alasan>."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /reject <payment_id> <alasan>")
        return
    try:
        pid = int(args[0])
    except ValueError:
        await update.message.reply_text("ID harus angka.")
        return

    note = " ".join(args[1:]) if len(args) > 1 else "Ditolak admin"
    payment = db.get_payment(pid)
    if not payment or payment["status"] != "pending":
        await update.message.reply_text(f"Pembayaran #{pid} tidak ditemukan atau sudah diproses.")
        return

    db.reject_payment(pid, note)
    await update.message.reply_text(f"❌ #{pid} ditolak: {note}")

    try:
        await context.bot.send_message(
            chat_id=payment["telegram_id"],
            text=f"❌ <b>Pembayaran Ditolak</b>\n\nAlasan: {note}",
            parse_mode="HTML",
        )
    except Exception:
        pass
