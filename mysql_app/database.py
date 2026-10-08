from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
MYSQL_VARIABLES = (
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
)


def mysql_url_from_env() -> URL:
    """Read project-root .env without overriding process environment."""
    file_settings = dotenv_values(ENV_FILE)
    settings = {
        key: os.environ.get(key, file_settings.get(key)) for key in MYSQL_VARIABLES
    }
    missing = [key for key, value in settings.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing MySQL configuration: "
            + ", ".join(missing)
            + ". Set these variables in the environment or project-root .env."
        )
    try:
        port = int(settings["MYSQL_PORT"])
    except ValueError as error:
        raise ValueError("MYSQL_PORT must be a valid integer") from error
    if not 1 <= port <= 65535:
        raise ValueError("MYSQL_PORT must be between 1 and 65535")
    return URL.create(
        "mysql+pymysql",
        username=settings["MYSQL_USER"],
        password=settings["MYSQL_PASSWORD"],
        host=settings["MYSQL_HOST"],
        port=port,
        database=settings["MYSQL_DATABASE"],
    )


class Base(DeclarativeBase):
    """Base class for MySQL ORM mappings."""


class SQLAlchemyDatabase:
    """Creates short-lived SQLAlchemy sessions for repository operations."""

    def __init__(self, database_url: str | URL | None = None) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    def initialize(self) -> None:
        from mysql_app.models.task_model import TaskModel

        Base.metadata.create_all(bind=self.engine, tables=[TaskModel.__table__])

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                self._database_url
                if self._database_url is not None
                else mysql_url_from_env()
            )
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
            )
        return self._session_factory

    def dispose(self) -> None:
        if self._engine is not None:
            self._engine.dispose()

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
        except BaseException:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()
