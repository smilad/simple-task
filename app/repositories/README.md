# لایهٔ Repository

Repository تنها لایه‌ای است که SQL پروژه را می‌نویسد. `TaskRepository` بین Entityهای Python و رکوردهای جدول `tasks` تبدیل انجام می‌دهد.

## وابستگی‌ها

```text
TaskRepository → SQLiteDatabase → sqlite3
TaskRepository → Task
```

Repository به FastAPI، `Request`، `HTTPException` یا مدل‌های Pydantic وابسته نیست.

## عملیات موجود

| متد | SQL/رفتار |
| --- | --- |
| `create(title)` | `INSERT` و برگرداندن `Task` تازه |
| `list()` | `SELECT` مرتب‌شده بر اساس `id` |
| `get_by_id(id)` | `SELECT` یک رکورد یا `None` |
| `update(...)` | `UPDATE` سپس خواندن رکورد جدید |
| `delete(id)` | `DELETE` و برگرداندن موفقیت/ناموفق‌بودن |

`_to_entity` تنها محل تبدیل `sqlite3.Row` به `Task` است. متمرکزکردن این تبدیل از پراکندن نام ستون‌ها در Service و Controller جلوگیری می‌کند.

## SQL امن و بدون ORM

مقدارهای ورودی هرگز به متن SQL چسبانده نمی‌شوند:

```python
connection.execute(
    "SELECT id, title, completed FROM tasks WHERE id = ?",
    (task_id,),
)
```

علامت `?` placeholder است و tuple دوم مقدار را جداگانه به SQLite می‌دهد. این الگو را برای هر مقدار خارجی حفظ کنید.

در `update` از `COALESCE(?, column)` استفاده شده است: مقدار `None` ستون قبلی را نگه می‌دارد، اما `False` برای `completed` همچنان مقدار معتبر `0` است و ذخیره می‌شود.

## تراکنش و اتصال

هر متد از `SQLiteDatabase.connection()` استفاده می‌کند. این context manager پس از عملیات موفق `commit` می‌کند، در خطا `rollback` می‌کند و در هر حالت اتصال را می‌بندد. Repository نباید خودش اتصال سراسری یا تراکنش پنهان بسازد.

## چه چیزی اینجا نیست؟

قانون‌هایی مثل «عنوان خالی نباشد» یا تصمیم «رکورد پیدا نشد چه پاسخ HTTPی داشته باشد» در Repository قرار نمی‌گیرند. این‌ها به‌ترتیب مسئولیت Service و Controller هستند.
