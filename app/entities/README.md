# لایهٔ Entity

Entity زبان مشترک دامنهٔ برنامه است: چیزی که برنامه درباره‌اش حرف می‌زند، نه شکل JSON آن و نه شکل ذخیره‌سازی آن در SQLite.

## نمونهٔ فعلی

`Task` در `task.py` سه واقعیت دامنه را نگه می‌دارد:

- `id`: شناسه‌ای که SQLite هنگام ذخیره‌سازی می‌سازد.
- `title`: عنوان کار.
- `completed`: وضعیت انجام‌شدن کار.

```python
@dataclass(frozen=True, slots=True)
class Task:
    id: int
    title: str
    completed: bool
```

## چرا `dataclass(frozen=True, slots=True)`؟

- `dataclass` مدل را کوچک و صریح نگه می‌دارد.
- `frozen=True` مانع تغییر تصادفی Entity پس از ساخت می‌شود؛ برای تغییر، Repository یک Entity جدید برمی‌گرداند.
- `slots=True` دیکشنری نمونه را حذف می‌کند و برای مدل‌های کوچک هزینهٔ حافظه را کم می‌کند.

## مرز این لایه

Entity نباید از FastAPI، Pydantic یا `sqlite3` import کند. همچنین نباید SQL اجرا کند یا از `Request` و `Response` خبر داشته باشد. اگر فردا HTTP با CLI یا پیام‌صف جایگزین شود، Entity باید بدون تغییر بماند.

## هنگام افزودن ویژگی جدید

اگر مثلاً `priority` اضافه شد، ابتدا آن را به Entity اضافه کنید. سپس تغییر لازم را به ترتیب در schema جدول SQLite، تبدیل `Row` در Repository، اعتبارسنجی Service و Schemaهای HTTP اعمال کنید. این ترتیب باعث می‌شود تغییر از مدل دامنه آغاز شود، نه از جزئیات انتقال داده.
