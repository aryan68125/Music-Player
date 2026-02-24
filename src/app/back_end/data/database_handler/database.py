import os
import sqlite3
import sys
from pathlib import Path


class DatabaseHandler:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = self._resolve_db_path(db_path)
        self._connection: sqlite3.Connection | None = None

    @staticmethod
    def _resolve_db_path(db_path: str | Path | None) -> Path:
        if db_path is not None:
            return Path(db_path)

        env_override = os.getenv("MUSIC_PLAYER_DB_PATH")
        if env_override:
            return Path(env_override)

        if sys.platform == "darwin":
            base_dir = Path.home() / "Library" / "Application Support"
        elif sys.platform == "win32":
            appdata = os.getenv("APPDATA")
            if appdata:
                base_dir = Path(appdata)
            else:
                base_dir = Path.home() / "AppData" / "Roaming"
        else:
            base_dir = Path(os.getenv("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))

        return base_dir / "MusicPlayer" / "app.db"

    def connect(self) -> sqlite3.Connection:
        if self._connection is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self.db_path)
            self._connection.execute("PRAGMA foreign_keys = ON;")
        return self._connection

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def initialize_schema(self) -> None:
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                title TEXT,
                artist TEXT,
                album TEXT,
                duration_ms INTEGER,
                is_favorite INTEGER NOT NULL DEFAULT 0,
                artwork_hash TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                kind TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, kind)
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                playlist_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (playlist_id, track_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
                UNIQUE(playlist_id, position)
            );
            """
        )
        connection.commit()

    def table_exists(self, table_name: str) -> bool:
        connection = self.connect()
        cursor = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1;",
            (table_name,),
        )
        return cursor.fetchone() is not None
