# OpenClaw SaaS Platform — Проект и Архитектура

> **Цель**: Развернуть OpenClaw как управляемый сервис (SaaS) для нетехнической аудитории.
> Клиенты оформляют подписку (стоимость VPS включена), получают личный сервер с OpenClaw и управляют им через Telegram-бот и веб-приложение (личный кабинет).

**Язык интерфейса**: Русский  
**Платёжные системы**: ЮKassa / Робокасса (в процессе выбора)  
**Приоритет MVP**: Telegram Bot + Backend

---

## 1. Общая архитектура

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                       │
│                                                         │
│   ┌──────────────────┐      ┌──────────────────────┐    │
│   │  Telegram Bot     │      │  Web App (Next.js)   │    │
│   │  (клиентский)     │      │  Личный кабинет      │    │
│   └────────┬─────────┘      └──────────┬───────────┘    │
└────────────┼───────────────────────────┼────────────────┘
             │                           │
             ▼                           ▼
┌─────────────────────────────────────────────────────────┐
│                    PLATFORM BACKEND                      │
│                                                         │
│   ┌───────────────────────────────────────────────┐     │
│   │           API Server (FastAPI / Python)        │     │
│   └──────┬──────────┬──────────────┬──────────────┘     │
│          │          │              │                     │
│   ┌──────▼───┐ ┌────▼─────┐ ┌─────▼──────────┐         │
│   │PostgreSQL│ │  Redis   │ │ Admin TG Bot   │         │
│   │  (данные)│ │(очереди) │ │(уведомления)   │         │
│   └──────────┘ └──────────┘ └────────────────┘         │
└─────────────────────┬───────────────────────────────────┘
                      │ SSH / Ansible
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   CUSTOMER SERVERS                       │
│                                                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│   │  VPS #1  │  │  VPS #2  │  │  VPS #N  │             │
│   │ OpenClaw │  │ OpenClaw │  │ OpenClaw │             │
│   └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Компоненты

| Компонент | Назначение |
|---|---|
| **Telegram Bot (клиентский)** | Точка входа: регистрация, оплата, статус сервера, базовые команды |
| **Web App (личный кабинет)** | Дашборд: управление сервером, настройки OpenClaw, логи, API-ключи |
| **API Server** | Центральный бэкенд: бизнес-логика, auth, управление серверами |
| **Admin TG Bot** | Уведомления операторам о заявках, ручные действия |
| **PostgreSQL** | Пользователи, подписки, серверы, платежи |
| **Redis** | Кэш сессий, очереди Celery, FSM бота |
| **VPS Instances** | Отдельные серверы клиентов с OpenClaw |

---

## 2. Технологический стек

| Слой | Технология |
|---|---|
| Backend API | **Python 3.12 + FastAPI** |
| Telegram Bot | **aiogram 3.x** (async, FSM, Telegram Web App) |
| Web Frontend | **Next.js 15** (React, SSR) |
| Database | **PostgreSQL 16** + **SQLAlchemy 2.0** (async) + **Alembic** |
| Task Queue | **Celery** + **Redis** |
| Server Management | **Paramiko** (SSH) + **Ansible** (provisioning) |
| Auth | **JWT** + **Telegram Login Widget** |
| Payments | **ЮKassa** / **Робокасса** |
| Deployment | **Docker Compose** (платформа), **Ubuntu 22.04** (VPS) |

---

## 3. Структура проекта

```
thermal-helix/
├── backend/                     # FastAPI + бизнес-логика
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings (Pydantic)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   │
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── subscription.py
│   │   │   ├── server.py
│   │   │   ├── payment.py
│   │   │   └── ticket.py
│   │   │
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── server.py
│   │   │   ├── subscription.py
│   │   │   └── payment.py
│   │   │
│   │   ├── api/                 # API routes
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── servers.py
│   │   │   │   ├── subscriptions.py
│   │   │   │   └── webhooks.py
│   │   │   └── deps.py          # Dependencies
│   │   │
│   │   ├── services/            # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── server_service.py
│   │   │   ├── subscription_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── provisioning_service.py
│   │   │   └── openclaw_service.py
│   │   │
│   │   ├── tasks/               # Celery async tasks
│   │   │   ├── server_tasks.py
│   │   │   └── notification_tasks.py
│   │   │
│   │   └── utils/
│   │       ├── ssh.py
│   │       └── helpers.py
│   │
│   ├── alembic/                 # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── bot/                         # Telegram Bot (aiogram)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── handlers/
│   │   │   ├── start.py         # /start + onboarding
│   │   │   ├── subscription.py  # Подписки и оплата
│   │   │   ├── server.py        # Статус сервера
│   │   │   ├── support.py       # Тикеты поддержки
│   │   │   └── admin.py         # Admin-only
│   │   │
│   │   ├── keyboards/
│   │   │   ├── main_menu.py
│   │   │   ├── subscription.py
│   │   │   └── server.py
│   │   │
│   │   ├── middlewares/
│   │   │   └── auth.py
│   │   │
│   │   ├── states/
│   │   │   └── onboarding.py
│   │   │
│   │   └── services/
│   │       └── api_client.py
│   │
│   └── Dockerfile
│
├── admin_bot/                   # Admin notification bot
│   ├── app/
│   │   ├── main.py
│   │   ├── handlers/
│   │   │   ├── tickets.py
│   │   │   └── servers.py
│   │   └── notifications.py
│   └── Dockerfile
│
├── frontend/                    # Next.js Web App
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx     # Главная дашборда
│   │   │   │   ├── server/
│   │   │   │   │   └── page.tsx # Управление сервером
│   │   │   │   ├── settings/
│   │   │   │   │   └── page.tsx # Настройки OpenClaw
│   │   │   │   ├── logs/
│   │   │   │   │   └── page.tsx # Логи
│   │   │   │   └── billing/
│   │   │   │       └── page.tsx # Подписка и платежи
│   │   │   └── api/
│   │   │
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── dashboard/
│   │   │   └── server/
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── telegram.ts
│   │   │   └── auth.ts
│   │   │
│   │   └── styles/
│   │       └── globals.css
│   │
│   ├── package.json
│   └── Dockerfile
│
├── ansible/                     # Server provisioning
│   ├── playbooks/
│   │   ├── setup_server.yml
│   │   ├── install_openclaw.yml
│   │   ├── configure_openclaw.yml
│   │   └── update_openclaw.yml
│   ├── inventory/
│   │   └── hosts.yml
│   └── roles/
│       └── openclaw/
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
└── README.md
```

---

## 4. Схема базы данных

### users
| Поле | Тип | Описание |
|---|---|---|
| id | int PK | |
| telegram_id | bigint UNIQUE | Telegram User ID |
| username | varchar | |
| first_name | varchar | |
| last_name | varchar | |
| email | varchar | |
| role | enum | client / admin / operator |
| created_at | datetime | |
| updated_at | datetime | |

### subscriptions
| Поле | Тип | Описание |
|---|---|---|
| id | int PK | |
| user_id | int FK → users | |
| plan | varchar | starter / pro / enterprise |
| status | enum | pending / active / expired / cancelled |
| starts_at | datetime | |
| expires_at | datetime | |
| auto_renew | boolean | |
| created_at | datetime | |

### servers
| Поле | Тип | Описание |
|---|---|---|
| id | int PK | |
| user_id | int FK → users | |
| subscription_id | int FK → subscriptions | |
| name | varchar | Имя сервера |
| provider | varchar | hetzner / contabo / custom |
| ip_address | varchar | |
| ssh_port | int | |
| status | enum | provisioning / configuring / active / stopped / error |
| openclaw_config | json | Текущая конфигурация |
| openclaw_version | varchar | |
| last_health_check | datetime | |
| created_at | datetime | |

### payments
| Поле | Тип | Описание |
|---|---|---|
| id | int PK | |
| user_id | int FK → users | |
| subscription_id | int FK → subscriptions | |
| amount | decimal | |
| currency | varchar | RUB |
| provider | varchar | yookassa / robokassa |
| external_id | varchar | ID в платёжной системе |
| status | enum | pending / completed / failed / refunded |
| created_at | datetime | |

### tickets
| Поле | Тип | Описание |
|---|---|---|
| id | int PK | |
| user_id | int FK → users | |
| server_id | int FK → servers (nullable) | |
| subject | varchar | |
| status | enum | open / in_progress / resolved / closed |
| description | text | |
| created_at | datetime | |
| resolved_at | datetime | |

### server_logs
| Поле | Тип | Описание |
|---|---|---|
| id | int PK | |
| server_id | int FK → servers | |
| action | varchar | start / stop / restart / config_update / health_check |
| result | varchar | success / failure |
| details | text | |
| created_at | datetime | |

### api_keys
| Поле | Тип | Описание |
|---|---|---|
| id | int PK | |
| server_id | int FK → servers | |
| provider | varchar | openai / anthropic / openrouter / gemini |
| key_masked | varchar | sk-...xxxx |
| key_encrypted | text | AES-256 зашифрованный ключ |
| added_at | datetime | |

---

## 5. Бизнес-процесс (полуавтоматическая система)

```
Клиент                  Telegram Bot         API Server        Admin Bot          Оператор
  │                          │                    │                 │                  │
  │── /start ───────────────▶│                    │                 │                  │
  │                          │── создать user ───▶│                 │                  │
  │◀─ Главное меню ─────────│                    │                 │                  │
  │                          │                    │                 │                  │
  │── Выбрать тариф ────────▶│                    │                 │                  │
  │── Оплатить ─────────────▶│── подписка ───────▶│                 │                  │
  │                          │                    │── 🔔 Заявка! ──▶│                  │
  │                          │                    │                 │── уведомление ──▶│
  │                          │                    │                 │                  │
  │                          │                    │                 │◀─ /assign_server │
  │                          │                    │◀── привязка ────│    {ip} {user}   │
  │                          │                    │                 │                  │
  │                          │                    │═══ SSH/Ansible ═══════════════════▶│
  │                          │                    │   (автонастройка OpenClaw)         VPS
  │                          │                    │                 │                  │
  │                          │                    │                 │◀─ /add_keys ─────│
  │                          │                    │   (ручное добавление API ключей)   │
  │                          │                    │                 │                  │
  │◀─ ✅ Сервер готов! ──────│◀── уведомление ───│                 │                  │
  │                          │                    │                 │                  │
  │── Открыть ЛК ───────────▶ Web App (дашборд)  │                 │                  │
```

---

## 6. Telegram Bot — Команды

### Клиентские команды
| Команда | Описание |
|---|---|
| `/start` | Регистрация / главное меню |
| `/subscribe` | Выбор и оплата тарифа |
| `/status` | Статус сервера (online/offline, uptime, RAM/CPU) |
| `/restart` | Перезапустить OpenClaw |
| `/logs` | Последние логи OpenClaw |
| `/dashboard` | Открыть Web App (inline button) |
| `/support` | Создать тикет в поддержку |
| `/profile` | Информация об аккаунте и подписке |

### Команды администратора (Admin Bot)
| Команда | Описание |
|---|---|
| `/tickets` | Список открытых заявок |
| `/assign_server {ip} {user_id}` | Привязать VPS к клиенту |
| `/provision {server_id}` | Запустить автонастройку |
| `/add_keys {server_id}` | Добавить API-ключи (FSM-диалог) |
| `/server_status {server_id}` | Полный статус сервера |
| `/broadcast {message}` | Рассылка всем клиентам |

---

## 7. Web App (Личный кабинет) — Страницы

### 7.1. Dashboard (главная)
- Статус сервера: 🟢 Online / 🔴 Offline
- Uptime, CPU, RAM, Disk (графики)
- Версия OpenClaw
- Быстрые действия: Restart, Stop, Update

### 7.2. Управление сервером
- Start / Stop / Restart OpenClaw
- Обновить OpenClaw до последней версии
- `openclaw doctor` output
- Настройка каналов (Telegram, WhatsApp…)

### 7.3. Настройки
- Редактирование `openclaw.json` через UI-форму
- Управление моделями (провайдер, fallback)
- Управление API-ключами
- Настройки безопасности (dmPolicy, allowFrom)

### 7.4. Логи
- Real-time логи Gateway (WebSocket)
- Фильтрация по уровню (info/warn/error)
- История действий

### 7.5. Подписка и оплата
- Текущий план и срок
- История платежей
- Продление / смена тарифа

### 7.6. Поддержка
- Создание тикета
- История тикетов
- Чат с оператором

---

## 8. API Endpoints

### Auth
```
POST /api/v1/auth/telegram       # Авторизация через Telegram initData
POST /api/v1/auth/refresh        # Обновление JWT
```

### Users
```
GET  /api/v1/users/me            # Текущий пользователь
PUT  /api/v1/users/me            # Обновление профиля
```

### Subscriptions
```
GET  /api/v1/subscriptions/plans           # Список тарифов
POST /api/v1/subscriptions                 # Создать подписку
GET  /api/v1/subscriptions/current         # Текущая подписка
POST /api/v1/subscriptions/current/cancel  # Отменить
```

### Servers
```
GET  /api/v1/servers/my              # Мой сервер
POST /api/v1/servers/my/restart      # Перезапуск
POST /api/v1/servers/my/stop         # Остановка
POST /api/v1/servers/my/update       # Обновление OpenClaw
GET  /api/v1/servers/my/status       # Метрики (CPU, RAM)
GET  /api/v1/servers/my/logs         # Логи
GET  /api/v1/servers/my/config       # Конфигурация
PUT  /api/v1/servers/my/config       # Обновить конфигурацию
GET  /api/v1/servers/my/doctor       # openclaw doctor
```

### API Keys
```
GET    /api/v1/servers/my/keys       # Список ключей (masked)
POST   /api/v1/servers/my/keys       # Добавить
DELETE /api/v1/servers/my/keys/{id}  # Удалить
```

### Payments
```
POST /api/v1/payments/create         # Создать платёж
GET  /api/v1/payments/history        # История
POST /api/v1/webhooks/payment        # Webhook от ЮKassa/Робокасса
```

### Admin
```
GET  /api/v1/admin/tickets              # Все тикеты
PUT  /api/v1/admin/tickets/{id}         # Обновить тикет
POST /api/v1/admin/servers              # Привязать VPS
POST /api/v1/admin/servers/{id}/provision # Запустить provisioning
GET  /api/v1/admin/users                # Все пользователи
GET  /api/v1/admin/stats                # Статистика
```

---

## 9. Интеграция с OpenClaw (SSH)

```python
class OpenClawService:
    """Управление OpenClaw на удалённом VPS через SSH"""
    
    async def get_status(self, server) -> dict:
        """systemctl status openclaw + openclaw doctor"""
        
    async def restart(self, server) -> bool:
        """systemctl restart openclaw"""
        
    async def get_logs(self, server, lines=100) -> str:
        """journalctl -u openclaw -n {lines}"""
        
    async def update_config(self, server, config: dict) -> bool:
        """Записать ~/.openclaw/openclaw.json через SFTP"""
        
    async def update_openclaw(self, server) -> bool:
        """npm update -g openclaw@latest + openclaw doctor"""
        
    async def get_metrics(self, server) -> dict:
        """CPU, RAM, Disk через SSH (top, free, df)"""
        
    async def add_api_key(self, server, provider, key) -> bool:
        """Добавить ключ в openclaw.json → env section"""
```

---

## 10. Provisioning Pipeline (Ansible)

```
[Новый VPS] → [Базовая настройка] → [Установка OpenClaw] → [Конфигурация] → [Запуск]

Базовая настройка:
  • Обновление Ubuntu
  • Установка Node.js 22
  • Установка Docker
  • Настройка firewall (ufw)
  • SSH hardening

Установка OpenClaw:
  • npm install -g openclaw
  • openclaw onboard (non-interactive)
  • Установка systemd daemon

Конфигурация:
  • Генерация openclaw.json
  • Настройка каналов
  • Привязка Telegram бота клиента

Запуск:
  • systemctl enable openclaw
  • Health check
  • Уведомление клиента
```

---

## 11. Безопасность

| Аспект | Решение |
|---|---|
| SSH-ключи | Ed25519, хранятся зашифрованно в БД |
| API-ключи клиентов | AES-256 шифрование, расшифровка только при записи на VPS |
| JWT | RS256, TTL 15 мин + refresh tokens |
| Telegram Auth | Валидация `initData` hash |
| VPS access | Только через платформу, прямой SSH закрыт для клиента |
| Gateway | Привязка к `127.0.0.1`, доступ через reverse proxy |

---

## 12. Порядок разработки (этапы)

### Этап 1 — MVP (2-3 недели) ⭐ ПРИОРИТЕТ
- [ ] Backend: Auth + Users + Subscriptions + Server models
- [ ] Telegram Bot: /start, /subscribe, /status, /restart
- [ ] Admin Bot: Уведомления о заявках, /assign_server
- [ ] Ansible: Базовый playbook для установки OpenClaw
- [ ] Интеграция с ЮKassa/Робокасса (тестовый режим)
- [ ] Docker Compose для dev-окружения

### Этап 2 — Личный кабинет (2-3 недели)
- [ ] Web App: Dashboard + Server Management + Logs
- [ ] SSH-интеграция: restart, logs, metrics
- [ ] Telegram Web App интеграция
- [ ] Расширенные метрики сервера

### Этап 3 — Полный функционал (2-3 недели)
- [ ] Web App: Configuration editor, API keys management
- [ ] Real-time логи через WebSocket
- [ ] Система тикетов (bot + web)
- [ ] Улучшенный auto-provisioning

### Этап 4 — Полировка и масштабирование
- [ ] Мониторинг здоровья серверов (cron-based)
- [ ] Auto-renewal подписок
- [ ] Статистика и аналитика для админов
- [ ] Документация для клиентов
