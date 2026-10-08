# نمونه‌های مستقل FastAPI برای مدیریت وظایف

چهار برنامهٔ مستقل، هرکدام با لایه‌های controller، service، repository، entity و schema:

| برنامه | ذخیره‌سازی | درگاه پیش‌فرض در مثال‌ها |
| --- | --- | --- |
| `app/` | SQLite با `sqlite3` و SQL، بدون ORM | 8000 |
| `orm_app/` | SQLite با SQLAlchemy ORM در `data/orm_tasks.db` | 8001 |
| `mysql_app/` | MySQL با SQLAlchemy ORM | 8002 |
| `redis_celery_app/` | Redis برای وظایف و Celery برای تکمیل غیرهمزمان | 8003 |

هر چهار برنامه مسیرهای CRUD یکسان دارند: `POST /tasks`، `GET /tasks`،
`GET /tasks/{task_id}`، `PATCH /tasks/{task_id}` و `DELETE /tasks/{task_id}`.
هر برنامه باید روی پورت مستقل اجرا شود؛ داده‌های آن‌ها مشترک نیست.

## نصب

از ریشهٔ پروژه:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## اجرای نمونه‌های SQLite

```bash
.venv/bin/python -m uvicorn app.main:app --port 8000
.venv/bin/python -m uvicorn orm_app.main:app --port 8001
```

هر دستور را در ترمینال جداگانه اجرا کنید. برنامه‌ها در اولین اجرا پوشهٔ `data/`
و جدول خودشان را می‌سازند. `orm_app.main.create_app(database_url=...)` نیز URL
دیگری برای آزمایش یا استقرار می‌پذیرد.

## اجرای MySQL

یک پایگاه دادهٔ MySQL بسازید و به کاربر اجازهٔ ایجاد جدول و خواندن/نوشتن بدهید.
متغیرهای `MYSQL_HOST`، `MYSQL_PORT`، `MYSQL_USER`، `MYSQL_PASSWORD` و
`MYSQL_DATABASE` را در محیط تنظیم کنید، یا `.env.example` را به `.env` کپی کرده
و مقادیر آن را تنظیم کنید. متغیرهای محیطی بر `.env` اولویت دارند.

```bash
.venv/bin/python -m uvicorn mysql_app.main:app --port 8002
```

برنامه هنگام راه‌اندازی جدول `tasks` را در پایگاه دادهٔ انتخاب‌شده ایجاد می‌کند؛
در صورت نبود تنظیمات یا در دسترس نبودن MySQL، راه‌اندازی ناموفق خواهد بود.

## اجرای Redis و Celery

ابتدا Redis را اجرا کنید. API و worker باید یک `REDIS_URL` مشترک داشته باشند.
برای هر دو ترمینال، متغیر محیطی را تنظیم کنید:

```bash
export REDIS_URL=redis://localhost:6379/0
.venv/bin/python -m uvicorn redis_celery_app.main:app --port 8003
```

در ترمینال دیگر:

```bash
export REDIS_URL=redis://localhost:6379/0
.venv/bin/python -m celery -A redis_celery_app.celery_app:celery_app worker --loglevel=info
```

در صورت نیاز، `CELERY_BROKER_URL` و `CELERY_RESULT_BACKEND` را نیز تنظیم کنید؛
پیش‌فرض هر دو `REDIS_URL` است. این نسخه Redis URL را از محیط می‌خواند، نه `.env`.
API برای تکمیل غیرهمزمان یک وظیفه، `POST /tasks/{task_id}/completion-jobs` را
با پاسخ `202` و `job_id` ارائه می‌دهد. وضعیت را با
`GET /tasks/{task_id}/completion-jobs/{job_id}` بخوانید؛ بعد از اجرای worker،
وضعیت `SUCCESS` و فیلد `completed: true` برمی‌گردد. نتیجهٔ job پس از ۲۴ ساعت
منقضی می‌شود. برای نگهداری پایدار داده‌ها Redis را با persistence و سیاست
حافظهٔ مناسب پیکربندی کنید؛ worker بدون Redis و broker اجرا نمی‌شود.

مستندات تعاملی هر برنامه در `/docs` روی پورت همان برنامه در دسترس است.
راهنمای لایه‌های برنامهٔ بدون ORM در [app/README.md](app/README.md) است.
