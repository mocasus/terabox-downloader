"""Database migrations — run on startup to ensure schema is current."""
import sqlite3
import logging

logger = logging.getLogger(__name__)

__all__ = ["migrate"]


def migrate(db_path: str) -> None:
    """Auto-migrate database schema: create missing tables and columns.

    Safe to run on every startup — uses IF NOT EXISTS and
    per-column existence checks.

    Args:
        db_path: Path to SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    try:
        # ── Create tables if not exist ──
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

        # ── Column-level migrations ──
        # Check existing columns and add any that are missing
        cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        user_migrations = {
            "is_vip": "ALTER TABLE users ADD COLUMN is_vip INTEGER DEFAULT 0",
            "vip_expiry": "ALTER TABLE users ADD COLUMN vip_expiry TEXT",
            "total_downloads": "ALTER TABLE users ADD COLUMN total_downloads INTEGER DEFAULT 0",
        }
        for col, sql in user_migrations.items():
            if col not in cols:
                logger.info(f"Migrating users table: adding {col}")
                conn.execute(sql)

        pay_cols = [r[1] for r in conn.execute("PRAGMA table_info(payments)").fetchall()]
        pay_migrations = {
            "order_id": "ALTER TABLE payments ADD COLUMN order_id TEXT UNIQUE",
            "signature": "ALTER TABLE payments ADD COLUMN signature TEXT",
        }
        for col, sql in pay_migrations.items():
            if col not in pay_cols:
                logger.info(f"Migrating payments table: adding {col}")
                conn.execute(sql)

        conn.commit()
        logger.info("Database migration complete")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()
