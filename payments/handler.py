"""Payment handler — process VIP purchases."""
from config import config
from database.models import db


async def handle_payment(bot, user_id: int, amount: int, method: str = "manual",
                         proof_file_id: str = None) -> int:
    """
    Record payment and notify admins.
    Returns payment_id.
    """
    payment_id = db.create_payment(user_id, amount, method, proof_file_id)

    # Notify all admins
    for admin_id in config.ADMIN_IDS:
        try:
            text = (
                f"💳 <b>Pembayaran Baru</b>\n\n"
                f"🆔 ID: <code>{payment_id}</code>\n"
                f"👤 User: <code>{user_id}</code>\n"
                f"💰 Jumlah: Rp {amount:,}\n"
                f"📲 Metode: {method}\n\n"
                f"Gunakan:\n"
                f"/approve {payment_id} — Setujui\n"
                f"/reject {payment_id} <alasan> — Tolak"
            )
            if proof_file_id:
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=proof_file_id,
                    caption=text,
                    parse_mode="HTML",
                )
            else:
                await bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode="HTML",
                )
        except Exception:
            pass

    return payment_id


def format_vip_info() -> str:
    """Format VIP pricing info for /vip command."""
    duration = config.VIP_DURATION_DAYS
    dur_text = "Lifetime" if duration == 0 else f"{duration} hari"

    text = (
        "💎 <b>TERABOX DOWNLOADER VIP</b>\n\n"
        "🔓 Akses unlimited download file Terabox\n"
        "⚡ No speed limit\n"
        "📂 Support folder & multi-file\n"
        "🎯 Direct link langsung\n\n"
        f"💰 <b>Harga: Rp {config.VIP_PRICE:,} / {dur_text}</b>\n\n"
    )

    if config.VIP_TRIAL_ENABLED:
        text += (
            f"🎁 <b>Free Trial:</b> {config.VIP_TRIAL_DOWNLOADS}x download gratis\n"
            "    Cobain dulu sebelum beli!\n\n"
        )

    text += (
        "📲 <b>Cara bayar:</b>\n"
        "1. Transfer sesuai nominal di atas\n"
        "2. Screenshot bukti transfer\n"
        "3. Kirim ke bot dengan perintah:\n"
        "   <code>/bayar</code>\n\n"
        "❓ Ada pertanyaan? Chat admin."
    )

    return text


async def verify_payment_auto(transaction_id: str) -> bool:
    """Auto-verify payment via callback (stub)."""
    return False
