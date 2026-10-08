"""Atomic Redis writes for task entities and completion-job lookup."""

from redis import Redis

from redis_celery_app.entities.task import Task

_PREFIX = "redis_celery_app"
_COUNTER = f"{_PREFIX}:tasks:next_id"
_IDS = f"{_PREFIX}:tasks:ids"

# INCR never expires; IDs are not reused after deletion, including delayed worker messages.
# Lua keeps each multi-key mutation indivisible across API processes and workers.
_CREATE = """
local id = redis.call('INCR', KEYS[1])
local key = ARGV[1] .. id
while redis.call('EXISTS', key) == 1 do
    id = redis.call('INCR', KEYS[1])
    key = ARGV[1] .. id
end
redis.call('HSET', key, 'title', ARGV[2], 'completed', '0')
redis.call('ZADD', KEYS[2], id, id)
return id
"""
_UPDATE = """
if redis.call('EXISTS', KEYS[1]) == 0 then return nil end
if ARGV[1] ~= '' then redis.call('HSET', KEYS[1], 'title', ARGV[1]) end
if ARGV[2] ~= '' then redis.call('HSET', KEYS[1], 'completed', ARGV[2]) end
return {redis.call('HGET', KEYS[1], 'title'), redis.call('HGET', KEYS[1], 'completed')}
"""
_DELETE = """
if redis.call('DEL', KEYS[1]) == 0 then return 0 end
redis.call('ZREM', KEYS[2], ARGV[1])
return 1
"""


class TaskRepository:
    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client
        self._create = redis_client.register_script(_CREATE)
        self._update = redis_client.register_script(_UPDATE)
        self._delete = redis_client.register_script(_DELETE)

    @staticmethod
    def _key(task_id: int) -> str:
        return f"{_PREFIX}:task:{task_id}"

    @staticmethod
    def _job_key(job_id: str) -> str:
        return f"{_PREFIX}:job:{job_id}"

    def create(self, title: str) -> Task:
        task_id = int(self._create(keys=[_COUNTER, _IDS], args=[f"{_PREFIX}:task:", title]))
        return Task(id=task_id, title=title, completed=False)

    def list(self) -> list[Task]:
        ids = self._redis.zrange(_IDS, 0, -1)
        if not ids:
            return []
        with self._redis.pipeline(transaction=False) as pipe:
            for task_id in ids:
                pipe.hgetall(self._key(int(task_id)))
            rows = pipe.execute()
        # A concurrent delete may occur between reading the index and the hashes.
        return [self._to_entity(int(task_id), row) for task_id, row in zip(ids, rows) if row]

    def get_by_id(self, task_id: int) -> Task | None:
        row = self._redis.hgetall(self._key(task_id))
        return self._to_entity(task_id, row) if row else None

    def update(
        self, task_id: int, *, title: str | None = None, completed: bool | None = None
    ) -> Task | None:
        fields = self._update(
            keys=[self._key(task_id)],
            args=[title if title is not None else "", "" if completed is None else str(int(completed))],
        )
        if fields is None:
            return None
        return Task(id=task_id, title=fields[0], completed=fields[1] == "1")

    def delete(self, task_id: int) -> bool:
        return bool(self._delete(keys=[self._key(task_id), _IDS], args=[task_id]))

    def record_job(self, job_id: str, task_id: int, *, ttl_seconds: int) -> None:
        if not self._redis.set(self._job_key(job_id), task_id, ex=ttl_seconds, nx=True):
            raise RuntimeError("Completion job ID collision")

    def get_job_task_id(self, job_id: str) -> int | None:
        value = self._redis.get(self._job_key(job_id))
        return int(value) if value is not None else None

    @staticmethod
    def _to_entity(task_id: int, row: dict[str, str]) -> Task:
        return Task(id=task_id, title=row["title"], completed=row["completed"] == "1")
