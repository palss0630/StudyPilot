"""
Memory store – high-level API over SQLite for sessions, messages, notes, quizzes.

Provides both short-term memory (recent messages) and long-term memory
(notes retrieved by keyword similarity).
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.studypilot.config import SHORT_TERM_MEMORY_MESSAGES, logger
from src.studypilot.memory.db import get_connection, init_db


class MemoryStore:
    """Unified memory store for StudyPilot."""

    def __init__(self, db_path=None) -> None:
        self._db_path = db_path
        init_db(db_path)

    @property
    def _conn(self):
        return get_connection(self._db_path)

    # ----- Sessions -----

    def create_session(self, goal: str = "", title: str = "Untitled") -> str:
        """Create a new session and return its ID."""
        session_id = uuid.uuid4().hex[:12]
        self._conn.execute(
            "INSERT INTO sessions (id, title, goal) VALUES (?, ?, ?)",
            (session_id, title, goal),
        )
        self._conn.commit()
        logger.debug("Created session %s", session_id)
        return session_id

    def update_session_title(self, session_id: str, title: str) -> None:
        """Update a session's title."""
        self._conn.execute(
            "UPDATE sessions SET title = ?, updated_at = datetime('now') WHERE id = ?",
            (title, session_id),
        )
        self._conn.commit()

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent sessions ordered by most recent first."""
        rows = self._conn.execute(
            "SELECT id, title, goal, created_at FROM sessions ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_session(self, session_id: str) -> None:
        """Delete a session and its associated messages."""
        self._conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        self._conn.commit()

    # ----- Messages -----

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to a session."""
        self._conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )
        self._conn.execute(
            "UPDATE sessions SET updated_at = datetime('now') WHERE id = ?",
            (session_id,),
        )
        self._conn.commit()

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get messages for a session, optionally limited to the last N."""
        limit = limit or SHORT_TERM_MEMORY_MESSAGES
        rows = self._conn.execute(
            """SELECT role, content FROM messages
               WHERE session_id = ?
               ORDER BY id DESC LIMIT ?""",
            (session_id, limit),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    # ----- Notes (long-term memory) -----

    def save_note(self, title: str, content: str, tags: str = "") -> int:
        """Save a note and return its ID."""
        cursor = self._conn.execute(
            "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags),
        )
        self._conn.commit()
        logger.debug("Saved note '%s' (id=%d)", title, cursor.lastrowid)
        return cursor.lastrowid  # type: ignore[return-value]

    def search_notes(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search notes by keyword (simple LIKE matching).

        This is intentionally simple – no embedding model needed.
        """
        pattern = f"%{query}%"
        rows = self._conn.execute(
            """SELECT id, title, content, tags, created_at FROM notes
               WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
               ORDER BY updated_at DESC LIMIT ?""",
            (pattern, pattern, pattern, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_notes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all notes, most recent first."""
        rows = self._conn.execute(
            "SELECT id, title, content, tags, created_at FROM notes ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_note(self, note_id: int) -> None:
        """Delete a note by ID."""
        self._conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self._conn.commit()

    # ----- Quiz Results -----

    def save_quiz_result(
        self,
        topic: str,
        score: int,
        total: int,
        session_id: Optional[str] = None,
        details: Optional[Dict] = None,
    ) -> int:
        """Save a quiz result and return its ID."""
        cursor = self._conn.execute(
            "INSERT INTO quiz_results (session_id, topic, score, total, details) VALUES (?, ?, ?, ?, ?)",
            (session_id, topic, score, total, json.dumps(details or {})),
        )
        self._conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def get_quiz_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get quiz result history."""
        rows = self._conn.execute(
            "SELECT id, session_id, topic, score, total, created_at FROM quiz_results ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ----- Tool Logs -----

    def log_tool_call(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
        output: str,
        duration_ms: int = 0,
        session_id: Optional[str] = None,
    ) -> None:
        """Log a tool invocation for debugging and transparency."""
        self._conn.execute(
            "INSERT INTO tool_logs (session_id, tool_name, inputs, output, duration_ms) VALUES (?, ?, ?, ?, ?)",
            (session_id, tool_name, json.dumps(inputs), output[:5000], duration_ms),
        )
        self._conn.commit()

    # ----- Long-term memory retrieval -----

    def retrieve_relevant_context(self, goal: str, limit: int = 3) -> str:
        """
        Retrieve relevant past notes for a goal to include in the planning prompt.

        Uses simple keyword extraction and LIKE matching.
        """
        # Extract keywords (words > 3 chars, skip common words)
        stop_words = {
            "about", "that", "this", "what", "with", "from", "have", "will",
            "your", "they", "been", "were", "said", "each", "which", "their",
            "then", "them", "than", "into", "some", "could", "other", "more",
            "very", "when", "come", "make", "like", "just", "over", "such",
            "also", "back", "after", "would", "only", "these", "give", "most",
            "tell", "teach", "learn", "explain", "compare", "and", "the", "for",
        }
        words = [
            w.strip(".,!?\"'()[]{}") for w in goal.lower().split()
            if len(w.strip(".,!?\"'()[]{}")) > 3
            and w.strip(".,!?\"'()[]{}") not in stop_words
        ]

        if not words:
            return ""

        results: List[Dict[str, Any]] = []
        seen_ids: set = set()
        for word in words[:5]:
            notes = self.search_notes(word, limit=limit)
            for note in notes:
                if note["id"] not in seen_ids:
                    seen_ids.add(note["id"])
                    results.append(note)

        if not results:
            return ""

        context_parts = []
        for note in results[:limit]:
            snippet = note["content"][:500]
            context_parts.append(f"- **{note['title']}**: {snippet}")

        return "**Relevant past notes:**\n" + "\n".join(context_parts)
