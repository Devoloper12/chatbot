"""
=============================================================================
Database Module: SQLite Persistence for Chat Memory & Sessions
=============================================================================
Manages persistent local storage for multi-session conversations, message
history, full-text search, and markdown/text export functionality.
=============================================================================
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import DB_FILE, EXPORTS_DIR


class ChatDatabase:
    """Handles all SQLite interactions for sessions and conversation history."""

    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Creates and returns a connection with foreign key support enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        """Initializes database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Sessions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Messages Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    duration_seconds REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                );
            """)

            # Index for fast session lookup and search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id, created_at);
            """)
            conn.commit()

    def get_or_create_active_session(self) -> Tuple[int, str]:
        """
        Retrieves the most recently updated session, or creates a new one
        if the database is currently empty.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM sessions ORDER BY updated_at DESC LIMIT 1;")
            row = cursor.fetchone()
            if row:
                return row["id"], row["title"]

        # If no session exists, create the initial session
        return self.create_session(title="General CS & Programming")

    def create_session(self, title: Optional[str] = None) -> Tuple[int, str]:
        """Creates a new chat session."""
        if not title or not title.strip():
            timestamp = datetime.now().strftime("%b %d, %H:%M")
            title = f"Chat Session ({timestamp})"
        else:
            title = title.strip()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (title, created_at, updated_at) VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);",
                (title,)
            )
            session_id = cursor.lastrowid
            conn.commit()
            return session_id, title

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Returns all chat sessions with their message counts and timestamps."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id, 
                    s.title, 
                    s.created_at, 
                    s.updated_at,
                    COUNT(m.id) AS message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                GROUP BY s.id
                ORDER BY s.updated_at DESC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def session_exists(self, session_id: int) -> bool:
        """Checks if a given session ID exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM sessions WHERE id = ?;", (session_id,))
            return cursor.fetchone() is not None

    def get_session_title(self, session_id: int) -> Optional[str]:
        """Returns the title of a specific session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM sessions WHERE id = ?;", (session_id,))
            row = cursor.fetchone()
            return row["title"] if row else None

    def delete_session(self, session_id: int) -> bool:
        """Deletes a session and its associated messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?;", (session_id,))
            conn.commit()
            return cursor.rowcount > 0

    def add_message(self, session_id: int, role: str, content: str, duration: float = 0.0) -> None:
        """Appends a user or bot message to the session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (session_id, role, content, duration_seconds, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);
            """, (session_id, role, content, duration))

            # Update the session's updated_at timestamp
            cursor.execute("""
                UPDATE sessions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?;
            """, (session_id,))
            conn.commit()

    def get_session_messages(self, session_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves messages for a session in chronological order."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, role, content, duration_seconds, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC
            """
            if limit:
                query += f" LIMIT {int(limit)}"
            cursor.execute(query, (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def clear_session_messages(self, session_id: int) -> None:
        """Removes all messages in a session while keeping the session entry."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?;", (session_id,))
            cursor.execute("""
                UPDATE sessions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?;
            """, (session_id,))
            conn.commit()

    def search_messages(self, query: str) -> List[Dict[str, Any]]:
        """Searches for keyword matches across all saved messages."""
        clean_query = f"%{query.strip()}%"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    m.id, 
                    m.session_id, 
                    s.title AS session_title, 
                    m.role, 
                    m.content, 
                    m.created_at
                FROM messages m
                JOIN sessions s ON m.session_id = s.id
                WHERE m.content LIKE ?
                ORDER BY m.created_at DESC
                LIMIT 20;
            """, (clean_query,))
            return [dict(row) for row in cursor.fetchall()]

    def export_session(self, session_id: int, export_format: str = "markdown") -> Optional[Path]:
        """Exports a conversation session to a file in the exports directory."""
        title = self.get_session_title(session_id)
        if not title:
            return None

        messages = self.get_session_messages(session_id)
        sanitized_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format.lower() in ("txt", "text"):
            filename = f"session_{session_id}_{sanitized_title}_{timestamp}.txt"
            export_path = EXPORTS_DIR / filename
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(f"SESSION: {title} (ID: {session_id})\n")
                f.write(f"EXPORTED AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                for msg in messages:
                    prefix = "YOU" if msg["role"] == "user" else "BOT"
                    timing = f" [{msg['duration_seconds']:.2f}s]" if msg.get("duration_seconds") else ""
                    f.write(f"[{msg['created_at']}] {prefix}{timing}:\n")
                    f.write(f"{msg['content']}\n\n")
                    f.write("-" * 40 + "\n\n")
        else:
            filename = f"session_{session_id}_{sanitized_title}_{timestamp}.md"
            export_path = EXPORTS_DIR / filename
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(f"# 💬 Conversation Export: {title}\n\n")
                f.write(f"- **Session ID:** `{session_id}`\n")
                f.write(f"- **Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- **Total Messages:** {len(messages)}\n\n")
                f.write("---\n\n")
                for msg in messages:
                    if msg["role"] == "user":
                        f.write(f"### 🧑 You ({msg['created_at']})\n\n")
                        f.write(f"{msg['content']}\n\n")
                    else:
                        timing = f" *(generated in {msg['duration_seconds']:.2f}s)*" if msg.get("duration_seconds") else ""
                        f.write(f"### 🤖 Bot{timing}\n\n")
                        f.write(f"{msg['content']}\n\n")
                    f.write("---\n\n")

        return export_path

    def get_database_stats(self) -> Dict[str, Any]:
        """Returns summary statistics for the /about command."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sessions;")
            total_sessions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM messages;")
            total_messages = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM messages WHERE role = 'user';")
            user_messages = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM messages WHERE role = 'bot';")
            bot_messages = cursor.fetchone()[0]

            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "user_messages": user_messages,
                "bot_messages": bot_messages,
            }
