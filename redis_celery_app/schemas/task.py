from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from redis_celery_app.entities.completion_job import CompletionJob
from redis_celery_app.entities.task import Task


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Task title must not be blank")
        return normalized


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Task title must not be blank")
        return normalized

    @model_validator(mode="after")
    def require_change(self) -> Self:
        if self.title is None and self.completed is None:
            raise ValueError("At least one task field must be provided")
        return self


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool

    @classmethod
    def from_entity(cls, task: Task) -> Self:
        return cls(id=task.id, title=task.title, completed=task.completed)


class CompletionJobResponse(BaseModel):
    job_id: str
    task_id: int
    state: str
    task: TaskResponse | None = None
    error: str | None = None

    @classmethod
    def from_entity(cls, job: CompletionJob) -> Self:
        return cls(
            job_id=job.job_id,
            task_id=job.task_id,
            state=job.state,
            task=TaskResponse.from_entity(job.task) if job.task is not None else None,
            error=job.error,
        )
