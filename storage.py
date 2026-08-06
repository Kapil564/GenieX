import os
import sqlite3
from typing import Any, Dict, Optional


class Storage:
    def __init__(self, path: str = "data/store.db") -> None:
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
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                value TEXT,
                file_id TEXT,
                caption TEXT
            )
            """
        )
        self.connection.commit()

    def add_item(
        self,
        name: str,
        kind: str,
        value: str,
        file_id: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        item_id = self._unique_key(name)
        self.connection.execute(
            """
            INSERT INTO items (id, name, type, value, file_id, caption)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item_id, name, kind, value, file_id, caption),
        )
        self.connection.commit()
        return {
            "id": item_id,
            "name": name,
            "type": kind,
            "value": value,
            "file_id": file_id,
            "caption": caption,
        }

    def get_item(self, lookup: str) -> Optional[Dict[str, Any]]:
        row = self.connection.execute(
            "SELECT id, name, type, value, file_id, caption FROM items WHERE id = ? OR name = ?",
            (lookup, lookup),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def list_items(self) -> list[Dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT id, name, type, value, file_id, caption FROM items ORDER BY name"
        ).fetchall()
        return [dict(row) for row in rows]

    def _unique_key(self, name: str) -> str:
        base = name.lower().replace(" ", "-")
        candidate = base
        index = 1
        while self._exists(candidate):
            candidate = f"{base}-{index}"
            index += 1
        return candidate

    def _exists(self, item_id: str) -> bool:
        row = self.connection.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone()
        return row is not None
