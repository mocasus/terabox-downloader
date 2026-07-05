"""Database migrations — run on startup."""
import sqlite3


def migrate(db_path: str):
    """Auto-migrate: create missing tables/columns."""
    conn = sqlite3.connect(db_path)
    try:
        # Ensure tables exist
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
                amount          INTEGER NOT NULL,
                method          TEXT DEFAULT 'manual',
                proof_file      TEXT,
                status          TEXT DEFAULT 'pending',
                admin_note      TEXT,
                created_at      TEXT DEFAULT (datetime('now','localtime')),
                processed_at    TEXT
            );
        """)

        # Migrate: ensure is_vip column exists (safety check)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "is_vip" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN is_vip INTEGER DEFAULT 0")
        if "vip_expiry" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN vip_expiry TEXT")
        if "total_downloads" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN total_downloads INTEGER DEFAULT 0")

        conn.commit()
    finally:
        conn.close()
