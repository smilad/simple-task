# لایهٔ Schema

Schemaها قرارداد HTTP هستند، نه مدل دامنه و نه مدل SQL. این پروژه از مدل‌های Pydantic فقط برای خواندن، اعتبارسنجی و مستندسازی بدنه و پاسخ API استفاده می‌کند؛ Pydantic در اینجا ORM نیست.

## Schemaهای فعلی

| Schema | جهت | رفتار |
| --- | --- | --- |
| `TaskCreate` | ورودی `POST` | عنوان ۱ تا ۲۵۵ کاراکتر و غیرخالی پس از `strip` |
| `TaskUpdate` | ورودی `PATCH` | عنوان و/یا `completed`؛ حداقل یکی باید مقدار داشته باشد |
| `TaskResponse` | خروجی | `id`، `title` و `completed` |

## چرا Entity و Schema جدا هستند؟

`Task` برای منطق دامنه ساخته شده است. `TaskCreate` و `TaskUpdate` شکل JSON ورودی را کنترل می‌کنند و `TaskResponse` قرارداد خروجی را ثابت نگه می‌دارد. اگر در آینده نام فیلد API تغییر کند یا یک فیلد داخلی نباید در پاسخ دیده شود، بدون تغییر Entity می‌توان Schema را تغییر داد.

```python
TaskResponse.from_entity(task)
```

این تبدیل صریح، عبور اتفاقی فیلدهای داخلی Entity به پاسخ HTTP را سخت‌تر می‌کند.

## اعتبارسنجی

- `Field(min_length=1, max_length=255)` طول عنوان را کنترل می‌کند.
- `field_validator` فاصله‌های ابتدا و انتهای عنوان را حذف و عنوان خالی را رد می‌کند.
- `model_validator` در `TaskUpdate` مانع PATCH بدون هیچ تغییر مؤثر می‌شود.

FastAPI از همین Schemaها برای تولید OpenAPI و صفحهٔ `/docs` استفاده می‌کند. قانون‌های حیاتی دامنه همچنان در Service نیز باقی می‌مانند تا اعتبارسنجی فقط به HTTP وابسته نباشد.
