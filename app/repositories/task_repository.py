import sqlite3

from app.database import SQLiteDatabase
from app.entities.task import Task


class TaskRepository:
    """Persists task entities with parameterized sqlite3 statements."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def create(self, title: str) -> Task:
        with self._database.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,),
            )
            task_id = cursor.lastrowid

        if task_id is None:
            raise RuntimeError("SQLite did not return an ID for the new task")
        return Task(id=task_id, title=title, completed=False)

    def list(self) -> list[Task]:
        with self._database.connection() as connection:
            rows = connection.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id"
            ).fetchall()
        return [self._to_entity(row) for row in rows]

    def get_by_id(self, task_id: int) -> Task | None:
        with self._database.connection() as connection:
            row = connection.execute(
                "SELECT id, title, completed FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        return self._to_entity(row) if row is not None else None

    def update(
        self,
        task_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Task | None:
        with self._database.connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET title = COALESCE(?, title), completed = COALESCE(?, completed)
                WHERE id = ?
                """,
                (title, completed, task_id),
            )
            if cursor.rowcount == 0:
                return None
            row = connection.execute(
                "SELECT id, title, completed FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        if row is None:
            raise RuntimeError("Updated task disappeared before it could be read")
        return self._to_entity(row)

    def delete(self, task_id: int) -> bool:
        with self._database.connection() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            completed=bool(row["completed"]),
        )
