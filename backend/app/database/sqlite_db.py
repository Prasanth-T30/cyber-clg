"""
FusionGuardNet – SQLite User Database
Lightweight persistent user store using Python's built-in sqlite3.
"""

import sqlite3
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "users.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT    UNIQUE NOT NULL,
                email           TEXT    UNIQUE NOT NULL,
                hashed_password TEXT    NOT NULL,
                full_name       TEXT    DEFAULT '',
                role            TEXT    DEFAULT 'analyst',
                is_active       INTEGER DEFAULT 1,
                created_at      REAL    DEFAULT (strftime('%s','now'))
            )
        """)
        conn.commit()
    logger.info("SQLite user DB ready at %s", DB_PATH)


def create_user(username: str, email: str, hashed_password: str,
                full_name: str = "", role: str = "analyst") -> Optional[Dict[str, Any]]:
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO users
                   (username, email, hashed_password, full_name, role, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (username.lower(), email.lower(), hashed_password,
                 full_name, role, time.time()),
            )
            conn.commit()
            return get_user_by_id(cursor.lastrowid)
    except sqlite3.IntegrityError:
        return None


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username.lower(),),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1",
            (email.lower(),),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def user_exists(username: str, email: str) -> Dict[str, bool]:
    with get_connection() as conn:
        u = conn.execute("SELECT id FROM users WHERE username = ?", (username.lower(),)).fetchone()
        e = conn.execute("SELECT id FROM users WHERE email = ?",    (email.lower(),)).fetchone()
    return {"username_taken": u is not None, "email_taken": e is not None}
