from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from redis import Redis

from redis_celery_app.celery_app import settings
from redis_celery_app.controllers.task_controller import create_task_router
from redis_celery_app.repositories.task_repository import TaskRepository
from redis_celery_app.services.task_service import TaskService


def create_app(redis_client: Redis | None = None) -> FastAPI:
    """Create the API; pass a client explicitly for isolated integration checks."""
    owned_client = redis_client is None
    client = redis_client if redis_client is not None else Redis.from_url(
        settings.redis_url, decode_responses=True
    )
    service = TaskService(TaskRepository(client))

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            client.ping()  # Fail at startup when persistence is unavailable.
            yield
        finally:
            if owned_client:
                client.close()

    app = FastAPI(title="Task API - Redis and Celery", version="1.0.0", lifespan=lifespan)
    app.include_router(create_task_router(service))
    return app


app = create_app()
