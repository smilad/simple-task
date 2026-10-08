from uuid import uuid4

from redis_celery_app.celery_app import celery_app
from redis_celery_app.entities.completion_job import CompletionJob
from redis_celery_app.entities.task import Task
from redis_celery_app.repositories.task_repository import TaskRepository
from redis_celery_app.worker_tasks import complete_task


class TaskNotFoundError(LookupError):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id} was not found")


class JobNotFoundError(LookupError):
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Completion job {job_id} was not found")


class TaskService:
    """Task CRUD and an asynchronous, idempotent completion use case."""

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
        self, task_id: int, *, title: str | None = None, completed: bool | None = None
    ) -> Task:
        if title is not None:
            title = self._normalize_title(title)
        task = self._repository.update(task_id, title=title, completed=completed)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def delete_task(self, task_id: int) -> None:
        if not self._repository.delete(task_id):
            raise TaskNotFoundError(task_id)

    def enqueue_completion(self, task_id: int) -> CompletionJob:
        self.get_task(task_id)
        job_id = uuid4().hex
        # Publish before acknowledging; a queued worker never depends on this metadata.
        # If the task is deleted after this check, its worker run fails rather than resurrects it.
        complete_task.apply_async(args=(task_id,), task_id=job_id)
        self._repository.record_job(job_id, task_id, ttl_seconds=86400)
        return CompletionJob(job_id=job_id, task_id=task_id, state="PENDING")

    def get_completion(self, task_id: int, job_id: str) -> CompletionJob:
        if self._repository.get_job_task_id(job_id) != task_id:
            raise JobNotFoundError(job_id)
        result = celery_app.AsyncResult(job_id)
        state = result.state
        if state == "SUCCESS":
            return CompletionJob(
                job_id=job_id, task_id=task_id, state=state, task=Task(**result.result)
            )
        if state == "FAILURE":
            return CompletionJob(
                job_id=job_id, task_id=task_id, state=state, error=str(result.result)
            )
        return CompletionJob(job_id=job_id, task_id=task_id, state=state)

    @staticmethod
    def _normalize_title(title: str) -> str:
        normalized = title.strip()
        if not normalized:
            raise ValueError("Task title must not be blank")
        return normalized
