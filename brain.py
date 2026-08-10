import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class BrainStore:
    """
    SQLite-backed storage for the GenieX Second Brain bot.

    Supports notes, voice transcripts, links, photos, videos, documents,
    auto-tagging, and full-text search via SQLite FTS5.
    """

    def __init__(self, path: str = "data/brain.db") -> None:
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._connect()
        self._init_schema()

    def _connect(self) -> None:
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row

    def _init_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                kind TEXT NOT NULL,
                content TEXT NOT NULL,
                file_id TEXT,
                caption TEXT,
                source_url TEXT,
                transcript TEXT
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                note_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                PRIMARY KEY (note_id, tag),
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
            )
            """
        )
        self.connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                content, transcript, source_url,
                content_rowid=rowid
            )
            """
        )
        self.connection.execute(
            """
            CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
                INSERT INTO notes_fts(rowid, content, transcript, source_url)
                VALUES (new.id, new.content, new.transcript, new.source_url);
            END
            """
        )
        self.connection.execute(
            """
            CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
                DELETE FROM notes_fts WHERE rowid = old.id;
            END
            """
        )
        self.connection.commit()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _extract_url(self, text: str) -> Optional[str]:
        match = re.search(r"https?://\S+", text)
        return match.group(0) if match else None

    def _extract_tags(self, text: str) -> List[str]:
        """
        Extract #hashtags from the text and infer a few common tags from content.
        """
        tags = {t.lower().lstrip("#").strip(".,!?") for t in re.findall(r"#\w+", text)}
        lowered = text.lower()

        keyword_tags = [
            ("idea", "idea"),
            ("todo", "todo"),
            ("task", "todo"),
            ("read", "read-later"),
            ("watch", "watch-later"),
            ("book", "book"),
            ("project", "project"),
            ("work", "work"),
            ("learn", "learning"),
            ("question", "question"),
            ("quote", "quote"),
            ("dream", "dream"),
        ]

        for keyword, tag in keyword_tags:
            if keyword in lowered:
                tags.add(tag)

        return sorted(tags)

    def add_note(
        self,
        user_id: int,
        kind: str,
        content: str,
        file_id: Optional[str] = None,
        caption: Optional[str] = None,
        transcript: Optional[str] = None,
    ) -> Dict[str, Any]:
        source_url = self._extract_url(content) or self._extract_url(caption or "")
        full_text = " ".join(
            filter(
                None,
                [content, caption, transcript],
            )
        )
        tags = self._extract_tags(full_text)

        cursor = self.connection.execute(
            """
            INSERT INTO notes (user_id, created_at, kind, content, file_id, caption, source_url, transcript)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, self._now(), kind, content, file_id, caption, source_url, transcript),
        )
        note_id = cursor.lastrowid

        if tags:
            self.connection.executemany(
                "INSERT OR IGNORE INTO tags (note_id, tag) VALUES (?, ?)",
                [(note_id, tag) for tag in tags],
            )

        self.connection.commit()

        return {
            "id": note_id,
            "user_id": user_id,
            "created_at": self._now(),
            "kind": kind,
            "content": content,
            "file_id": file_id,
            "caption": caption,
            "source_url": source_url,
            "transcript": transcript,
            "tags": tags,
        }

    def get_note(self, note_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        row = self.connection.execute(
            "SELECT * FROM notes WHERE id = ? AND user_id = ?",
            (note_id, user_id),
        ).fetchone()
        if not row:
            return None
        return self._with_tags(dict(row))

    def list_recent(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [self._with_tags(dict(row)) for row in rows]

    def search(self, user_id: int, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Try FTS first; fall back to LIKE if query is not FTS-friendly.
        try:
            rows = self.connection.execute(
                """
                SELECT n.* FROM notes n
                JOIN notes_fts fts ON n.id = fts.rowid
                WHERE n.user_id = ? AND notes_fts MATCH ?
                ORDER BY n.created_at DESC
                LIMIT ?
                """,
                (user_id, query, limit),
            ).fetchall()
        except sqlite3.Error:
            rows = []

        if not rows:
            pattern = f"%{query}%"
            rows = self.connection.execute(
                """
                SELECT * FROM notes
                WHERE user_id = ? AND (
                    content LIKE ? OR caption LIKE ? OR transcript LIKE ? OR source_url LIKE ?
                )
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, pattern, pattern, pattern, pattern, limit),
            ).fetchall()

        return [self._with_tags(dict(row)) for row in rows]

    def list_by_tag(self, user_id: int, tag: str, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT n.* FROM notes n
            JOIN tags t ON n.id = t.note_id
            WHERE n.user_id = ? AND t.tag = ?
            ORDER BY n.created_at DESC
            LIMIT ?
            """,
            (user_id, tag.lower(), limit),
        ).fetchall()
        return [self._with_tags(dict(row)) for row in rows]

    def list_tags(self, user_id: int, limit: int = 50) -> List[str]:
        rows = self.connection.execute(
            """
            SELECT DISTINCT t.tag FROM tags t
            JOIN notes n ON t.note_id = n.id
            WHERE n.user_id = ?
            ORDER BY t.tag
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [row["tag"] for row in rows]

    def today(self, user_id: int) -> List[Dict[str, Any]]:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rows = self.connection.execute(
            """
            SELECT * FROM notes
            WHERE user_id = ? AND created_at LIKE ?
            ORDER BY created_at DESC
            """,
            (user_id, f"{today}%"),
        ).fetchall()
        return [self._with_tags(dict(row)) for row in rows]

    def random(self, user_id: int) -> Optional[Dict[str, Any]]:
        row = self.connection.execute(
            "SELECT * FROM notes WHERE user_id = ? ORDER BY RANDOM() LIMIT 1",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        return self._with_tags(dict(row))

    def delete_note(self, note_id: int, user_id: int) -> bool:
        cursor = self.connection.execute(
            "DELETE FROM notes WHERE id = ? AND user_id = ?",
            (note_id, user_id),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def _with_tags(self, note: Dict[str, Any]) -> Dict[str, Any]:
        tags = self.connection.execute(
            "SELECT tag FROM tags WHERE note_id = ?",
            (note["id"],),
        ).fetchall()
        note["tags"] = [row["tag"] for row in tags]
        return note

    def __del__(self) -> None:
        try:
            self.connection.close()
        except Exception:
            pass
