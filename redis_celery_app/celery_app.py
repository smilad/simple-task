"""Run worker: celery -A redis_celery_app.celery_app:celery_app worker --loglevel=info."""

from celery import Celery

from redis_celery_app.config import Settings

settings = Settings.from_env()
celery_app = Celery(
    "redis_celery_app",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["redis_celery_app.worker_tasks"],
)
celery_app.conf.update(
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,
    result_backend_transport_options={"global_keyprefix": "redis_celery_app:"},
)
