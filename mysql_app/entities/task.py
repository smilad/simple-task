from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Task:
    """Domain representation of a persisted task."""

    id: int
    title: str
    completed: bool
