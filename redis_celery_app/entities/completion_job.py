from dataclasses import dataclass

from redis_celery_app.entities.task import Task


@dataclass(frozen=True, slots=True)
class CompletionJob:
    job_id: str
    task_id: int
    state: str
    task: Task | None = None
    error: str | None = None
