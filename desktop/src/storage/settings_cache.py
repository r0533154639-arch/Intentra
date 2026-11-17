from __future__ import annotations

import sqlite3
from pathlib import Path


class SettingsCache:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or Path.home() / ".intentra" / "settings_cache.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def set(self, key: str, value: str):
        self.connection.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)", (key, value))
        self.connection.commit()

    def get(self, key: str):
        row = self.connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def delete(self, key: str):
        self.connection.execute("DELETE FROM settings WHERE key = ?", (key,))
        self.connection.commit()

    def close(self):
        self.connection.close()
