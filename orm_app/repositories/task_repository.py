from sqlalchemy import select

from orm_app.database import SQLAlchemyDatabase
from orm_app.entities.task import Task
from orm_app.models.task_model import TaskModel


class TaskRepository:
    """Persists task entities through SQLAlchemy ORM sessions."""

    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def create(self, title: str) -> Task:
        with self._database.session() as session:
            model = TaskModel(title=title)
            session.add(model)
            session.flush()
            task = self._to_entity(model)
        return task

    def list(self) -> list[Task]:
        with self._database.session() as session:
            models = session.scalars(select(TaskModel).order_by(TaskModel.id)).all()
            return [self._to_entity(model) for model in models]

    def get_by_id(self, task_id: int) -> Task | None:
        with self._database.session() as session:
            model = session.get(TaskModel, task_id)
            return self._to_entity(model) if model is not None else None

    def update(
        self,
        task_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Task | None:
        with self._database.session() as session:
            model = session.get(TaskModel, task_id)
            if model is None:
                return None
            if title is not None:
                model.title = title
            if completed is not None:
                model.completed = completed
            session.flush()
            task = self._to_entity(model)
        return task

    def delete(self, task_id: int) -> bool:
        with self._database.session() as session:
            model = session.get(TaskModel, task_id)
            if model is None:
                return False
            session.delete(model)
            return True

    @staticmethod
    def _to_entity(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            completed=model.completed,
        )
