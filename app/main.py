from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI

from app.controllers.task_controller import create_task_router
from app.database import SQLiteDatabase
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "tasks.db"


def create_app(database_path: str | Path = DEFAULT_DATABASE_PATH) -> FastAPI:
    """Create the HTTP application and compose its layers."""

    database = SQLiteDatabase(database_path)
    service = TaskService(TaskRepository(database))

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        yield

    app = FastAPI(title="Task API", version="1.0.0", lifespan=lifespan)
    app.include_router(create_task_router(service))
    return app


app = create_app()
