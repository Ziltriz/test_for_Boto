Простой сервис сокращения ссылок на FastAPI + SQLite (без ORM).

Ручки:

- `POST /shorten` — принимает длинную ссылку → возвращает короткую
- `GET /{short_code}` — показывает HTML-страницу со статистикой (количество переходов, оригинальная ссылка)

## Технологии

- Python 3.13
- FastAPI
- Uvicorn
- aiosqlite
- Pydantic v2
- Jinja2 (для HTML-страницы статистики)
- Poetry
- Ruff (линтер + форматтер)
- mypy
- pytest + httpx

## Структура проекта

.
├── src/
│   ├── url_shortener/
│   │   ├── __init__.py
│   │   ├── main.py               # точка входа
│   │   ├── config.py             # настройки
│   │   ├── database.py           # инициализация БД
│   │   ├── models.py             # Pydantic модели
│   │   ├── schemas.py            # схемы запросов/ответов
│   │   ├── services.py           # бизнес-логика
│   │   ├── utils.py              # хелперы
│   │   └── db/
│   │       └── lite_client.py    # клиент для SQLite
│   └── templates/
│       └── link_stats.html       # шаблон страницы статистики
├── tests/
│   ├── __init__.py
│   └── test_shortener.py         # тесты
├── logs/                         # создаётся автоматически
├── shortener.db                  # создаётся автоматически
├── pyproject.toml
├── README.md
└── .gitignore

 **Установка и запуск**

### Требования

- Python 3.13
- Poetry

### Шаги

```bash
1. Разархивировать проект 

2. Установить зависимости
poetry install

3. Запустить сервер
poetry run uvicorn src.url_shortener.main:app --reload --port 8000
```

После запуска:

- Swagger: http://localhost:8000/docs

## Как пользоваться

### 1. Сократить ссылку

```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path?with=parameters"}'
```

Пример ответа:

```json
{
  "short_url": "http://localhost:8000/abc123_byzil",
  "original_url": "https://example.com/very/long/path?with=parameters"
}
```

### 2. Посмотреть статистику

Открой в браузере:

```
http://localhost:8000/abc123_byzil
```

Увидишь страницу с текстом примерно такого вида:

> Оригинальная ссылка: https://example.com/...
> По этой ссылке перешли 3 раза
> Создана: 2026-02-07 13:45

+ кнопка «Перейти по ссылке»

### Запуск тестов

```bash
poetry run pytest -v
# или с покрытием
poetry run pytest --cov=src/url_shortener
```

## Что реализовано

- Валидация URL через `HttpUrl`
- Генерация короткого кода
- Хранение в SQLite (без ORM, через aiosqlite)
- Подсчёт кликов
- Логирование (RotatingFileHandler, отдельные файлы)
- HTML-страница со статистикой вместо редиректа
- Базовые тесты (создание ссылки, просмотр статистики, 404)
- Чистая структура (роутеры / сервисы / db-клиент)
- pyproject.toml + Poetry + Ruff + mypy

## Что не сделано (но можно доработать)

- Автоматический 301-редирект вместо страницы статистики
- Возможность задать свой короткий код (custom alias)
- Rate limiting
- Переход на PostgreSQL + миграции
- Redis для кэша / счётчиков
- Удаление / редактирование ссылок
- Docker

## Комментарии к тестовому

Сделано за ~3.5–4 часа с учётом требований задания.Сфокусировался на:

- чистоте кода и структуры
- корректной работе эндпоинтов
- валидации
- тестах
- логировании
- читаемости и поддерживаемости

Прикольно спасибо за тестовое, все что лишнее это взято из другого моего проекта fast-api-backend-base. Не стал чистить так как время было ограничено
