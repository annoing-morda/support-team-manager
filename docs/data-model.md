# Модель данных

## Диаграмма связей (ER)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Employee   │       │    Duty     │       │   Absence   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ PK id       │──┐    │ PK id       │    ┌──│ PK id       │
│ telegram_id │  │    │ FK employee │────┘  │ FK employee │
│ username    │  └────│    _id      │       │    _id      │
│ full_name   │       │ date        │       │ start_date  │
│ is_admin    │       │ notified    │       │ end_date    │
│ is_active   │       │ created_at  │       │ reason      │
│ created_at  │       └─────────────┘       │ created_at  │
└─────────────┘                             └─────────────┘
```

---

## Фаза 1 — MVP

### Employee (Сотрудник)

| Атрибут | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| **id** | INTEGER | NO | PK, autoincrement |
| telegram_id | BIGINT | NO | Telegram user ID |
| username | VARCHAR(255) | YES | Telegram @username (без @) |
| full_name | VARCHAR(255) | NO | Имя пользователя в Telegram |
| is_admin | BOOLEAN | NO | Права администратора |
| is_active | BOOLEAN | NO | Активен ли сотрудник |
| created_at | TIMESTAMP | NO | Дата создания записи |

**Ключи и индексы:**
| Тип | Имя | Поля |
|-----|-----|------|
| PRIMARY KEY | pk_employees | id |
| UNIQUE | uq_employees_telegram_id | telegram_id |
| INDEX | ix_employees_telegram_id | telegram_id |

**Значения по умолчанию:**
- `is_admin` = FALSE
- `is_active` = TRUE
- `created_at` = NOW()

---

### Duty (Дежурство)

| Атрибут | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| **id** | INTEGER | NO | PK, autoincrement |
| employee_id | INTEGER | NO | FK → Employee.id |
| date | DATE | NO | Дата дежурства |
| notified | BOOLEAN | NO | Отправлено ли напоминание |
| created_at | TIMESTAMP | NO | Дата создания записи |

**Ключи и индексы:**
| Тип | Имя | Поля |
|-----|-----|------|
| PRIMARY KEY | pk_duties | id |
| FOREIGN KEY | fk_duties_employee | employee_id → employees.id |
| UNIQUE | uq_duties_date | date |
| INDEX | ix_duties_date | date |
| INDEX | ix_duties_employee_id | employee_id |

**Значения по умолчанию:**
- `notified` = FALSE
- `created_at` = NOW()

**Ограничения:**
- Один дежурный на одну дату (UNIQUE на date)
- При удалении Employee — CASCADE или RESTRICT (обсудить)

---

## Фаза 2 — Автоматизация

### Absence (Отсутствие)

| Атрибут | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| **id** | INTEGER | NO | PK, autoincrement |
| employee_id | INTEGER | NO | FK → Employee.id |
| start_date | DATE | NO | Начало отсутствия |
| end_date | DATE | NO | Конец отсутствия (включительно) |
| reason | VARCHAR(50) | YES | Причина: vacation, sick, other |
| created_at | TIMESTAMP | NO | Дата создания записи |

**Ключи и индексы:**
| Тип | Имя | Поля |
|-----|-----|------|
| PRIMARY KEY | pk_absences | id |
| FOREIGN KEY | fk_absences_employee | employee_id → employees.id |
| INDEX | ix_absences_employee_id | employee_id |
| INDEX | ix_absences_dates | start_date, end_date |

**Значения по умолчанию:**
- `created_at` = NOW()

**Ограничения (CHECK):**
- `end_date >= start_date`
- `reason IN ('vacation', 'sick', 'other')` или NULL

---

## Фаза 3 — Мониторинг (будущее)

### Incident (Инцидент)

| Атрибут | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| **id** | INTEGER | NO | PK, autoincrement |
| source | VARCHAR(20) | NO | Источник: email, jira |
| external_id | VARCHAR(255) | YES | ID в источнике (ticket key, message id) |
| title | VARCHAR(500) | NO | Заголовок |
| contour | VARCHAR(100) | YES | Контур (etl.corp, bi.prod, etc.) |
| assigned_to | INTEGER | YES | FK → Employee.id (кому назначен) |
| status | VARCHAR(20) | NO | new, in_progress, resolved, ignored |
| created_at | TIMESTAMP | NO | Дата создания |
| resolved_at | TIMESTAMP | YES | Дата закрытия |

**Ключи и индексы:**
| Тип | Имя | Поля |
|-----|-----|------|
| PRIMARY KEY | pk_incidents | id |
| FOREIGN KEY | fk_incidents_assigned | assigned_to → employees.id |
| UNIQUE | uq_incidents_source_ext | source, external_id |
| INDEX | ix_incidents_status | status |
| INDEX | ix_incidents_contour | contour |
| INDEX | ix_incidents_created | created_at |

---

## Фаза 4 — Справочники (Контуры)

### Contour (Контур)

| Атрибут | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| **id** | INTEGER | NO | PK, autoincrement |
| code | VARCHAR(100) | NO | Код контура (etl.corp) |
| name | VARCHAR(255) | NO | Человекочитаемое имя |
| owner_id | INTEGER | YES | FK → Employee.id (владелец экспертизы) |
| docs_url | VARCHAR(500) | YES | Ссылка на документацию |
| escalation_contact | VARCHAR(255) | YES | Контакт для эскалации |
| is_active | BOOLEAN | NO | Активен ли контур |

**Ключи и индексы:**
| Тип | Имя | Поля |
|-----|-----|------|
| PRIMARY KEY | pk_contours | id |
| FOREIGN KEY | fk_contours_owner | owner_id → employees.id |
| UNIQUE | uq_contours_code | code |

**Значения по умолчанию:**
- `is_active` = TRUE

---

## Соглашения по именованию

| Объект | Соглашение | Пример |
|--------|------------|--------|
| Таблицы | snake_case, множественное число | `employees`, `duties` |
| Колонки | snake_case | `telegram_id`, `created_at` |
| Primary Key | `pk_<table>` | `pk_employees` |
| Foreign Key | `fk_<table>_<ref>` | `fk_duties_employee` |
| Unique | `uq_<table>_<columns>` | `uq_employees_telegram_id` |
| Index | `ix_<table>_<columns>` | `ix_duties_date` |
| Check | `ck_<table>_<description>` | `ck_absences_dates` |
