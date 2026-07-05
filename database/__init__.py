"""Database layer — SQLite with thread-safe operations.

Provides a singleton Database instance with:
- Thread-safe connections via threading.local
- Context-managed transactions with auto-rollback
- User, payment, and VIP CRUD operations
- Statistics queries
"""

from .models import db, Database

__all__ = ["db", "Database"]
