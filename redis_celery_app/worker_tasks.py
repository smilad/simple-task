"""Worker-side use case: finish an existing task, never recreate a deleted task."""

from redis import Redis

from redis_celery_app.celery_app import celery_app, settings
from redis_celery_app.repositories.task_repository import TaskRepository


@celery_app.task(name="redis_celery_app.complete_task")
def complete_task(task_id: int) -> dict[str, int | str | bool]:
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        task = TaskRepository(client).update(task_id, completed=True)
        if task is None:
            raise LookupError(f"Task {task_id} was deleted before completion")
        return {"id": task.id, "title": task.title, "completed": task.completed}
    finally:
        client.close()
