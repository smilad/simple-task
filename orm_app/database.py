from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "orm_tasks.db"


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM mappings."""


class SQLAlchemyDatabase:
    """Creates short-lived SQLAlchemy sessions for repository operations."""

    def __init__(self, database_url: str | URL | None = None) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    def initialize(self) -> None:
        if self._database_url is None:
            DEFAULT_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        from orm_app.models.task_model import TaskModel

        Base.metadata.create_all(bind=self.engine, tables=[TaskModel.__table__])

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                self._database_url
                if self._database_url is not None
                else URL.create("sqlite+pysqlite", database=str(DEFAULT_DATABASE_PATH))
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
