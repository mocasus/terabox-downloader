"""Statistics formatting utilities."""
from database.models import db as database


def format_stats() -> str:
    s = database.get_stats()
    return (
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: {s['total_users']}\n"
        f"👑 VIP Users: {s['vip_users']}\n"
        f"🆕 New Today: {s['new_today']}\n"
        f"⏳ Pending Payments: {s['pending_payments']}"
    )


def format_vip_list() -> str:
    users = database.get_all_vip_users()
    if not users:
        return "Belum ada user VIP."
    lines = ["👑 <b>VIP Users:</b>\n"]
    for u in users:
        expiry = u.get("vip_expiry") or "Lifetime"
        lines.append(f"• <code>{u['telegram_id']}</code> — {u.get('username') or 'N/A'} — {expiry}")
    return "\n".join(lines)


def format_pending_list(payments: list[dict]) -> str:
    if not payments:
        return "✅ Tidak ada pembayaran pending."
    lines = ["💳 <b>Pending Payments:</b>\n"]
    for p in payments:
        lines.append(
            f"#{p['id']} | User: {p['telegram_id']} | Rp {p['amount']:,} | {p['created_at']}"
        )
    return "\n".join(lines)
