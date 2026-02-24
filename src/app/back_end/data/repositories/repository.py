from collections.abc import Sequence
from typing import Any

from app.back_end.data.database_handler.database import DatabaseHandler


class Repository:
    def __init__(self, db_handler: DatabaseHandler) -> None:
        self.db_handler = db_handler

    def execute(self, query: str, params: Sequence[Any] = ()) -> None:
        connection = self.db_handler.connect()
        connection.execute(query, params)
        connection.commit()

    def fetch_one(self, query: str, params: Sequence[Any] = ()) -> tuple[Any, ...] | None:
        connection = self.db_handler.connect()
        cursor = connection.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: Sequence[Any] = ()) -> list[tuple[Any, ...]]:
        connection = self.db_handler.connect()
        cursor = connection.execute(query, params)
        return cursor.fetchall()
