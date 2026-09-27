from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class SQLiteDatabase:
    """Creates short-lived SQLite connections for repository operations."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def initialize(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 255),
                    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
                )
                """
            )

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        except BaseException:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()
