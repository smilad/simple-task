# راهنمای پروژهٔ FastAPI با SQLite

این پروژه با معماری لایه‌ای و بدون ORM ساخته شده است. SQLite با ماژول استاندارد `sqlite3` و SQL پارامتری استفاده می‌شود.

## راهنمای آموزشی هر لایه

- [ساختار و ترکیب برنامه](app/README.md)
- [لایهٔ Entity](app/entities/README.md)
- [لایهٔ Repository](app/repositories/README.md)
- [لایهٔ Service](app/services/README.md)
- [لایهٔ Controller](app/controllers/README.md)
- [لایهٔ Schema](app/schemas/README.md)

## اجرا

```bash
python3 -m uvicorn main:app --reload
```

پس از اجرا، مستندات تعاملی API در `http://127.0.0.1:8000/docs` در دسترس است.
