from pathlib import Path

from app.back_end.data.database_handler.database import DatabaseHandler


def test_schema_tables_exist(tmp_path):
    db = DatabaseHandler(db_path=tmp_path / "app.db")
    db.initialize_schema()
    assert db.table_exists("tracks")
    assert db.table_exists("playlists")
    assert db.table_exists("playlist_tracks")
    db.close()


def test_table_exists_returns_false_for_unknown_table(tmp_path):
    db = DatabaseHandler(db_path=tmp_path / "app.db")
    db.initialize_schema()
    assert db.table_exists("unknown_table") is False
    db.close()


def test_schema_initialization_is_idempotent(tmp_path):
    db = DatabaseHandler(db_path=tmp_path / "app.db")
    db.initialize_schema()
    db.initialize_schema()
    assert db.table_exists("tracks")
    db.close()


def test_default_db_path_uses_platform_resolver(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    db = DatabaseHandler()
    assert db.db_path == tmp_path / "MusicPlayer" / "app.db"


def test_env_db_path_override_takes_precedence(monkeypatch, tmp_path):
    expected_path = tmp_path / "custom" / "music.sqlite3"
    monkeypatch.setenv("MUSIC_PLAYER_DB_PATH", str(expected_path))
    db = DatabaseHandler()
    assert db.db_path == expected_path
