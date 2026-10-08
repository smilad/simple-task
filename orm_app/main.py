from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.engine import URL

from fastapi import FastAPI

from orm_app.controllers.task_controller import create_task_router
from orm_app.database import SQLAlchemyDatabase
from orm_app.repositories.task_repository import TaskRepository
from orm_app.services.task_service import TaskService

def create_app(database_url: str | URL | None = None) -> FastAPI:
    """Create the SQLite-backed ORM application."""

    database = SQLAlchemyDatabase(database_url)
    service = TaskService(TaskRepository(database))

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            database.initialize()
            yield
        finally:
            database.dispose()

    app = FastAPI(title="Task API - SQLite ORM", version="1.0.0", lifespan=lifespan)
    app.include_router(create_task_router(service))
    return app


app = create_app()
