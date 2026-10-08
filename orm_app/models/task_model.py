from sqlalchemy import Boolean, CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from orm_app.database import Base


class TaskModel(Base):
    """SQLAlchemy ORM mapping for the tasks table."""

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "length(trim(title)) BETWEEN 1 AND 255",
            name="ck_tasks_title_length",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )
