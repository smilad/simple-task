from fastapi import APIRouter, HTTPException, status

from mysql_app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from mysql_app.services.task_service import TaskNotFoundError, TaskService


def create_task_router(service: TaskService) -> APIRouter:
    """Build task endpoints around one application service instance."""

    router = APIRouter(prefix="/tasks", tags=["tasks"])

    @router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    def create_task(payload: TaskCreate) -> TaskResponse:
        return TaskResponse.from_entity(service.create_task(payload.title))

    @router.get("", response_model=list[TaskResponse])
    def list_tasks() -> list[TaskResponse]:
        return [TaskResponse.from_entity(task) for task in service.list_tasks()]

    @router.get("/{task_id}", response_model=TaskResponse)
    def get_task(task_id: int) -> TaskResponse:
        return TaskResponse.from_entity(_get_task_or_404(service, task_id))

    @router.patch("/{task_id}", response_model=TaskResponse)
    def update_task(task_id: int, payload: TaskUpdate) -> TaskResponse:
        try:
            task = service.update_task(
                task_id,
                title=payload.title,
                completed=payload.completed,
            )
        except TaskNotFoundError as error:
            raise _not_found(error.task_id) from error
        return TaskResponse.from_entity(task)

    @router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_task(task_id: int) -> None:
        try:
            service.delete_task(task_id)
        except TaskNotFoundError as error:
            raise _not_found(error.task_id) from error

    return router


def _get_task_or_404(service: TaskService, task_id: int):
    try:
        return service.get_task(task_id)
    except TaskNotFoundError as error:
        raise _not_found(error.task_id) from error


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} was not found",
    )
