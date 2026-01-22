# Техническая документация

## Стек технологий

| Компонент | Технология | Версия | Примечание |
|-----------|------------|--------|------------|
| Язык | Python | 3.11+ | Async/await |
| Telegram API | aiogram | 3.x | Асинхронный фреймворк |
| ORM | SQLAlchemy | 2.x | Async-режим |
| База данных | PostgreSQL | 15+ | Продакшн-ready |
| Миграции | Alembic | — | Версионирование схемы БД |
| Конфигурация | pydantic-settings | — | Валидация .env |
| Планировщик | APScheduler | — | Для напоминаний и cron-задач |
| Контейнеризация | Docker | — | Dockerfile + docker-compose |

---

## Контейнеризация и деплой

### Принципы

1. **12-Factor App** — конфигурация через переменные окружения, логи в stdout
2. **Stateless** — бот не хранит состояние в памяти, всё в БД
3. **Health checks** — эндпоинт для проверки живости (для оркестратора)
4. **Graceful shutdown** — корректное завершение при SIGTERM

### Структура контейнеров

```
┌─────────────────────────────────────────────────┐
│                 docker-compose                  │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────────────┐ │
│  │     bot     │───▶│       postgres          │ │
│  │  (Python)   │    │   (PostgreSQL 15)       │ │
│  └─────────────┘    └─────────────────────────┘ │
│         │                      │                │
│         ▼                      ▼                │
│  ┌─────────────┐    ┌─────────────────────────┐ │
│  │   volumes   │    │   volumes               │ │
│  │  (logs, etc)│    │  (pgdata)               │ │
│  └─────────────┘    └─────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Dockerfile (best practices)

```dockerfile
# Используем multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.11-slim as runtime

# Не запускать от root
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Копируем wheel из builder
COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl && rm *.whl

USER appuser

# Health check (если добавим HTTP-эндпоинт)
# HEALTHCHECK --interval=30s --timeout=3s \
#   CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "bot"]
```

### docker-compose.yml

```yaml
version: "3.9"

services:
  bot:
    build: .
    restart: unless-stopped
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app-network

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-bot}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-support_bot}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER}"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

volumes:
  pgdata:

networks:
  app-network:
    driver: bridge
```

---

## Структура проекта

```
support-team-manager/
├── bot/                    # Основной код бота
│   ├── __init__.py
│   ├── __main__.py         # Точка входа (python -m bot)
│   ├── config.py           # Конфигурация (pydantic-settings)
│   ├── handlers/           # Обработчики команд Telegram
│   │   ├── __init__.py
│   │   ├── common.py       # /start, /help
│   │   ├── admin.py        # Команды администратора
│   │   └── duty.py         # Команды дежурств
│   ├── services/           # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── duty.py         # Логика дежурств
│   │   └── scheduler.py    # Планировщик напоминаний
│   ├── database/           # Слой работы с БД
│   │   ├── __init__.py
│   │   ├── models.py       # SQLAlchemy-модели
│   │   ├── session.py      # Async session factory
│   │   └── repositories/   # Паттерн Repository
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── employee.py
│   │       └── duty.py
│   └── utils/              # Вспомогательные функции
│       ├── __init__.py
│       └── datetime.py
├── migrations/             # Alembic-миграции
│   ├── env.py
│   └── versions/
├── tests/                  # Тесты
│   ├── __init__.py
│   ├── conftest.py
│   └── test_duty.py
├── docs/                   # Документация
│   ├── product.md          # Продуктовые требования
│   ├── tech.md             # Техническая документация
│   └── data-model.md       # Модель данных
├── plans/                  # Планы задач (для AI-агентов)
├── .env.example            # Шаблон переменных окружения
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml          # Зависимости и настройки
└── README.md
```

---

## Конфигурация

Все секреты хранятся в `.env` (не коммитится).

```env
# .env.example

# Telegram
BOT_TOKEN=your_telegram_bot_token

# PostgreSQL
POSTGRES_USER=bot
POSTGRES_PASSWORD=change_me_in_production
POSTGRES_DB=support_bot
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# App
ADMIN_IDS=123456789,987654321
REMINDER_HOUR=9
REMINDER_MINUTE=0
TZ=Europe/Moscow
LOG_LEVEL=INFO
```

---

## Архитектурные принципы

1. **Асинхронность везде** — БД, HTTP, Telegram API работают через `async`/`await`
2. **Repository Pattern** — изоляция логики доступа к данным от бизнес-логики
3. **Dependency Injection** — зависимости передаются явно (не глобальные объекты)
4. **Разделение слоёв:**
   - `handlers/` — только парсинг команд и формирование ответов
   - `services/` — бизнес-логика
   - `database/` — работа с БД
5. **Stateless** — состояние только в БД, бот можно перезапустить без потерь
6. **Idempotency** — операции безопасны при повторном выполнении

---

## Команды бота (MVP)

| Команда | Роль | Описание |
|---------|------|----------|
| `/start` | все | Приветствие, регистрация |
| `/help` | все | Список команд |
| `/duty` | все | Показать текущего дежурного |
| `/myduties` | сотрудник | Мои предстоящие дежурства |
| `/setduty <date> <@user>` | админ | Назначить дежурство |
| `/removeduty <date>` | админ | Снять дежурство |
| `/employees` | админ | Список сотрудников |
| `/addemployee <@user>` | админ | Добавить сотрудника |

---

## Запуск проекта

### С Docker (рекомендуется)

```bash
# 1. Скопировать и заполнить .env
cp .env.example .env

# 2. Запустить контейнеры
docker-compose up -d

# 3. Применить миграции
docker-compose exec bot alembic upgrade head

# 4. Посмотреть логи
docker-compose logs -f bot
```

### Локальная разработка (без Docker)

```bash
# 1. Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Установить зависимости
pip install -e ".[dev]"

# 3. Поднять PostgreSQL (например, через Docker)
docker run -d --name postgres-dev \
  -e POSTGRES_USER=bot \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=support_bot \
  -p 5432:5432 \
  postgres:15-alpine

# 4. Скопировать и заполнить .env
cp .env.example .env
# Установить DATABASE_URL=postgresql+asyncpg://bot:dev@localhost:5432/support_bot

# 5. Применить миграции
alembic upgrade head

# 6. Запустить бота
python -m bot
```

---

## Связанные документы

- [Модель данных](data-model.md) — схема БД, атрибуты, ключи, констрейнты
- [Продуктовые требования](product.md) — фазы, роли, функционал
