"""
SQLite database initialisation for StudyPilot.

Tables: sessions, messages, notes, quiz_results, tool_logs.
All tables are created automatically on first run.
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional

from src.studypilot.config import DB_PATH, logger

# Thread-local storage for connections
_local = threading.local()


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Get a thread-local SQLite connection.

    Args:
        db_path: Override database path (useful for testing).

    Returns:
        An open sqlite3.Connection with row_factory set to sqlite3.Row.
    """
    path = str(db_path or DB_PATH)
    if not hasattr(_local, "connections"):
        _local.connections = {}

    if path not in _local.connections:
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.connections[path] = conn

    return _local.connections[path]


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Create all required tables if they do not exist.

    Args:
        db_path: Override database path (useful for testing).
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL DEFAULT 'Untitled',
            goal        TEXT NOT NULL DEFAULT '',
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            role        TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system', 'tool')),
            content     TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS notes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            content     TEXT NOT NULL,
            tags        TEXT NOT NULL DEFAULT '',
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS quiz_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT REFERENCES sessions(id) ON DELETE SET NULL,
            topic       TEXT NOT NULL,
            score       INTEGER NOT NULL,
            total       INTEGER NOT NULL,
            details     TEXT NOT NULL DEFAULT '{}',
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tool_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT REFERENCES sessions(id) ON DELETE SET NULL,
            tool_name   TEXT NOT NULL,
            inputs      TEXT NOT NULL DEFAULT '{}',
            output      TEXT NOT NULL DEFAULT '',
            duration_ms INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_tool_logs_session ON tool_logs(session_id);
        CREATE INDEX IF NOT EXISTS idx_quiz_results_session ON quiz_results(session_id);
        CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
    """)

    conn.commit()
    logger.info("Database initialized at %s", db_path or DB_PATH)
