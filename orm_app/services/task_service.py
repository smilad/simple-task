from orm_app.entities.task import Task
from orm_app.repositories.task_repository import TaskRepository


class TaskNotFoundError(LookupError):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id} was not found")


class TaskService:
    """Owns task use cases and domain-level validation."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task(self, title: str) -> Task:
        return self._repository.create(self._normalize_title(title))

    def list_tasks(self) -> list[Task]:
        return self._repository.list()

    def get_task(self, task_id: int) -> Task:
        task = self._repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update_task(
        self,
        task_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        if title is not None:
            title = self._normalize_title(title)

        task = self._repository.update(
            task_id,
            title=title,
            completed=completed,
        )
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def delete_task(self, task_id: int) -> None:
        if not self._repository.delete(task_id):
            raise TaskNotFoundError(task_id)

    @staticmethod
    def _normalize_title(title: str) -> str:
        normalized = title.strip()
        if not normalized:
            raise ValueError("Task title must not be blank")
        return normalized
