"""Database layer — SQLite with thread-safe operations."""
import sqlite3
import threading
from datetime import datetime, timedelta
from contextlib import contextmanager


class Database:
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._local = threading.local()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
        return self._local.conn

    @contextmanager
    def _tx(self):
        with self._lock:
            conn = self._get_conn()
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    # ── INIT ───────────────────────────────────────────

    def init(self):
        with self._lock:
            conn = self._get_conn()
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id     BIGINT UNIQUE NOT NULL,
                    username        TEXT,
                    full_name       TEXT,
                    is_vip          INTEGER DEFAULT 0,
                    vip_expiry      TEXT,
                    total_downloads INTEGER DEFAULT 0,
                    joined_at       TEXT DEFAULT (datetime('now','localtime'))
                );

                CREATE TABLE IF NOT EXISTS payments (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id     BIGINT NOT NULL,
                    order_id        TEXT UNIQUE,
                    amount          INTEGER NOT NULL,
                    method          TEXT DEFAULT 'klikqris',
                    proof_file      TEXT,
                    signature       TEXT,
                    status          TEXT DEFAULT 'pending',
                    admin_note      TEXT,
                    created_at      TEXT DEFAULT (datetime('now','localtime')),
                    processed_at    TEXT
                );
            """)
            conn.commit()

    # ── USERS ──────────────────────────────────────────

    def get_user(self, telegram_id: int) -> dict | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return dict(row) if row else None

    def create_user(self, telegram_id: int, username: str = None, full_name: str = None):
        with self._tx() as conn:
            conn.execute(
                """INSERT OR IGNORE INTO users (telegram_id, username, full_name)
                   VALUES (?, ?, ?)""",
                (telegram_id, username, full_name),
            )

    def is_vip(self, telegram_id: int) -> bool:
        user = self.get_user(telegram_id)
        if not user or not user["is_vip"]:
            return False
        expiry = user.get("vip_expiry")
        if expiry:
            try:
                exp_dt = datetime.fromisoformat(expiry)
                if exp_dt < datetime.now():
                    return False
            except (ValueError, TypeError):
                return False
        return True

    def get_vip_expiry(self, telegram_id: int) -> str | None:
        user = self.get_user(telegram_id)
        if not user:
            return None
        return user.get("vip_expiry")

    def get_remaining_days(self, telegram_id: int) -> int | None:
        """Returns remaining VIP days, None if lifetime, 0 if expired/not VIP."""
        user = self.get_user(telegram_id)
        if not user or not user["is_vip"]:
            return 0
        expiry = user.get("vip_expiry")
        if not expiry:
            return None  # lifetime
        try:
            exp_dt = datetime.fromisoformat(expiry)
            remaining = (exp_dt - datetime.now()).days
            return max(0, remaining)
        except (ValueError, TypeError):
            return 0

    def set_vip(self, telegram_id: int, days: int = 30):
        """Set VIP for N days. days=0 means lifetime."""
        with self._tx() as conn:
            # Ensure user exists
            conn.execute(
                "INSERT OR IGNORE INTO users (telegram_id) VALUES (?)",
                (telegram_id,),
            )
            if days == 0:
                conn.execute(
                    "UPDATE users SET is_vip=1, vip_expiry=NULL WHERE telegram_id=?",
                    (telegram_id,),
                )
            else:
                expiry = (datetime.now() + timedelta(days=days)).isoformat()
                conn.execute(
                    "UPDATE users SET is_vip=1, vip_expiry=? WHERE telegram_id=?",
                    (expiry, telegram_id),
                )

    def remove_vip(self, telegram_id: int):
        with self._tx() as conn:
            conn.execute(
                "UPDATE users SET is_vip=0, vip_expiry=NULL WHERE telegram_id=?",
                (telegram_id,),
            )

    def add_download_count(self, telegram_id: int):
        with self._tx() as conn:
            conn.execute(
                "UPDATE users SET total_downloads = total_downloads + 1 WHERE telegram_id=?",
                (telegram_id,),
            )

    # ── PAYMENTS ───────────────────────────────────────

    def create_payment(self, telegram_id: int, amount: int, method: str = "klikqris",
                        order_id: str = None, signature: str = None) -> int:
        with self._tx() as conn:
            cur = conn.execute(
                """INSERT INTO payments (telegram_id, order_id, amount, method, signature)
                   VALUES (?, ?, ?, ?, ?)""",
                (telegram_id, order_id, amount, method, signature),
            )
            return cur.lastrowid

    def get_pending_payments(self) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM payments WHERE status='pending' ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def approve_payment(self, payment_id: int):
        with self._tx() as conn:
            conn.execute(
                """UPDATE payments SET status='approved',
                   processed_at=datetime('now','localtime') WHERE id=?""",
                (payment_id,),
            )

    def reject_payment(self, payment_id: int, note: str = ""):
        with self._tx() as conn:
            conn.execute(
                """UPDATE payments SET status='rejected', admin_note=?,
                   processed_at=datetime('now','localtime') WHERE id=?""",
                (note, payment_id),
            )

    def get_payment(self, payment_id: int) -> dict | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM payments WHERE id=?", (payment_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_payment_by_order_id(self, order_id: str) -> dict | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM payments WHERE order_id=?", (order_id,)
        ).fetchone()
        return dict(row) if row else None

    def approve_payment_by_order_id(self, order_id: str):
        with self._tx() as conn:
            conn.execute(
                """UPDATE payments SET status='approved',
                   processed_at=datetime('now','localtime') WHERE order_id=?""",
                (order_id,),
            )

    def get_user_pending_payment(self, telegram_id: int) -> dict | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM payments WHERE telegram_id=? AND status='pending' ORDER BY created_at DESC LIMIT 1",
            (telegram_id,),
        ).fetchone()
        return dict(row) if row else None

    # ── ADMIN / STATS ──────────────────────────────────

    def get_all_vip_users(self) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM users WHERE is_vip=1 ORDER BY vip_expiry DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
        vip = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_vip=1").fetchone()["c"]
        today = datetime.now().strftime("%Y-%m-%d")
        downloads_today = conn.execute(
            "SELECT COUNT(*) as c FROM users WHERE joined_at LIKE ?",
            (f"{today}%",),
        ).fetchone()["c"]
        pending = conn.execute(
            "SELECT COUNT(*) as c FROM payments WHERE status='pending'"
        ).fetchone()["c"]
        return {
            "total_users": total,
            "vip_users": vip,
            "new_today": downloads_today,
            "pending_payments": pending,
        }

    def get_free_downloads_used(self, telegram_id: int) -> int:
        """Count downloads by this user today (for trial tracking)."""
        conn = self._get_conn()
        today = datetime.now().strftime("%Y-%m-%d")
        # We approximate by checking today's joined_at — in production you'd want a downloads table
        # For now return total_downloads as a proxy
        row = conn.execute(
            "SELECT total_downloads FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()
        return row["total_downloads"] if row else 0

    def get_all_users(self) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute("SELECT telegram_id FROM users").fetchall()
        return [dict(r) for r in rows]


# Global DB instance
db = Database()
