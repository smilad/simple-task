# لایهٔ Controller

Controller مرز HTTP برنامه است. `create_task_router` یک `APIRouter` می‌سازد و یک `TaskService` را دریافت می‌کند؛ بنابراین Controller به جای ساختن Repository یا اتصال SQLite، فقط از Service آماده استفاده می‌کند.

## مسیرها

| مسیر | عملیات | پاسخ موفق |
| --- | --- | --- |
| `POST /tasks` | ساخت Task | `201` |
| `GET /tasks` | فهرست Taskها | `200` |
| `GET /tasks/{task_id}` | خواندن یک Task | `200` |
| `PATCH /tasks/{task_id}` | تغییر عنوان یا وضعیت | `200` |
| `DELETE /tasks/{task_id}` | حذف Task | `204` |

## جریان Controller

1. FastAPI JSON را به `TaskCreate` یا `TaskUpdate` تبدیل و اعتبارسنجی می‌کند.
2. تابع مسیر Service را فراخوانی می‌کند.
3. Entity برگشتی با `TaskResponse.from_entity` به پاسخ HTTP تبدیل می‌شود.
4. `TaskNotFoundError` به `HTTPException` با وضعیت `404` ترجمه می‌شود.

خطای اعتبارسنجی Schema پیش از ورود به تابع مسیر رخ می‌دهد و FastAPI پاسخ `422` می‌دهد.

## مرز این لایه

Controller نباید SQL اجرا کند، جدول بسازد یا قانون کسب‌وکار را تکرار کند. برای نمونه، Controller نمی‌سنجد که عنوان خالی است؛ آن کار را Schema و Service انجام می‌دهند. همچنین Controller نباید `sqlite3.Row` را مستقیم به JSON تبدیل کند؛ Repository باید ابتدا آن را به Entity تبدیل کند.

## چرا Router factory؟

امضای `create_task_router(service)` وابستگی را صریح می‌کند. `app/main.py` در محل composition، `TaskRepository` و `TaskService` را می‌سازد و سپس Router را ثبت می‌کند. در نتیجه Controller وابستگی پنهان یا singleton داخلی ندارد.
