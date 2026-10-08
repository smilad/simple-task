from fastapi import APIRouter, HTTPException, status

from redis_celery_app.schemas.task import (
    CompletionJobResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from redis_celery_app.services.task_service import (
    JobNotFoundError,
    TaskNotFoundError,
    TaskService,
)


def create_task_router(service: TaskService) -> APIRouter:
    router = APIRouter(prefix="/tasks", tags=["tasks"])

    @router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    def create_task(payload: TaskCreate) -> TaskResponse:
        return TaskResponse.from_entity(service.create_task(payload.title))

    @router.get("", response_model=list[TaskResponse])
    def list_tasks() -> list[TaskResponse]:
        return [TaskResponse.from_entity(task) for task in service.list_tasks()]

    @router.get("/{task_id}", response_model=TaskResponse)
    def get_task(task_id: int) -> TaskResponse:
        try:
            return TaskResponse.from_entity(service.get_task(task_id))
        except TaskNotFoundError as error:
            raise _not_found(error.task_id) from error

    @router.patch("/{task_id}", response_model=TaskResponse)
    def update_task(task_id: int, payload: TaskUpdate) -> TaskResponse:
        try:
            task = service.update_task(task_id, title=payload.title, completed=payload.completed)
        except TaskNotFoundError as error:
            raise _not_found(error.task_id) from error
        return TaskResponse.from_entity(task)

    @router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_task(task_id: int) -> None:
        try:
            service.delete_task(task_id)
        except TaskNotFoundError as error:
            raise _not_found(error.task_id) from error

    @router.post(
        "/{task_id}/completion-jobs",
        response_model=CompletionJobResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def enqueue_completion(task_id: int) -> CompletionJobResponse:
        try:
            return CompletionJobResponse.from_entity(service.enqueue_completion(task_id))
        except TaskNotFoundError as error:
            raise _not_found(error.task_id) from error

    @router.get("/{task_id}/completion-jobs/{job_id}", response_model=CompletionJobResponse)
    def get_completion(task_id: int, job_id: str) -> CompletionJobResponse:
        try:
            return CompletionJobResponse.from_entity(service.get_completion(task_id, job_id))
        except JobNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            ) from error

    return router


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} was not found"
    )
