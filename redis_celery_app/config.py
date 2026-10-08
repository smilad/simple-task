cr"""Settings shared by the API process and the Celery worker."""

import os
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True, slots=True)
class Settings:
    redis_url: str
    broker_url: str
    result_backend: str

    @classmethod
    def from_env(cls) -> "Settings":
        redis_url = os.environ.get("REDIS_URL", "").strip()
        if not redis_url:
            raise RuntimeError("REDIS_URL must be set to a Redis URL (for example redis://localhost:6379/0)")
        broker_url = os.environ.get("CELERY_BROKER_URL", redis_url).strip()
        result_backend = os.environ.get("CELERY_RESULT_BACKEND", redis_url).strip()
        for name, url in (
            ("REDIS_URL", redis_url),
            ("CELERY_BROKER_URL", broker_url),
            ("CELERY_RESULT_BACKEND", result_backend),
        ):
            if urlsplit(url).scheme not in {"redis", "rediss"} or not urlsplit(url).hostname:
                raise RuntimeError(f"{name} must be a redis:// or rediss:// URL with a host")
        return cls(redis_url=redis_url, broker_url=broker_url, result_backend=result_backend)
