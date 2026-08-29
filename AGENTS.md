# AGENTS.md — IT-TOP Bot Async

## Что это
Telegram-бот для студентов IT-TOP (журнал, оценки, ДЗ, расписание). Прокси к `msapi.top-academy.ru`, решает проблемы официального сайта (падения, релогины). Стек: `aiogram` + `FastAPI` + `PostgreSQL` + `Docker`.

## Стек
- Python 3.13 (Docker `python:3.13.7-slim`), локально 3.14 по `.venv/pyvenv.cfg`
- `aiogram` — бот, `Dispatcher`/`Router` + FSM (`aiogram.fsm`)
- `FastAPI` + `uvicorn` — раздача HTML-оценок (`src/bot/main_functions/marks/upload.py`)
- `httpx` — запросы к Journal API
- `SQLAlchemy[asyncio]` + `asyncpg` + `PostgreSQL 15.15` — две таблицы
- `APScheduler (AsyncIOScheduler, TZ=Asia/Krasnoyarsk)` — уведомления
- `jinja2`, `watchdog`, `psutil`, `python-multipart`
- Контейнеризация: `Docker` + `docker-compose.yml` (services: `bot`, `database`)

## Точка входа
`main.py` — единственный entrypoint (Docker `ENTRYPOINT ["python", "./main.py"]`):
```python
asyncio.gather(db_obj.init_db(), settings_db_obj.init_db(), start_api(), start_bot())
```
- `start_api()` — `uvicorn.Server(app, host=0.0.0.0:8000)` — FastAPI из `upload.py`
- `start_bot()` — `dp.startup.register(init_notifications)` + `dp.start_polling(bot)`
- `bot`, `dp`, `db_obj`, `settings_db_obj` — синглтоны из `src/storage.py`

## Структура
```
main.py
src/
  storage.py                  # глобальные синглтоны: bot, dp, db_obj, settings_db_obj, dict-хранилища, scheduler
  api/Journal_API.py          # класс API — обёртка над msapi.top-academy.ru
  db/Journal_database.py      # Creds_db, Settings_db
  templates/marks.html        # шаблон оценок
  bot/
    bot_main.py               # сборка всех Router → dp.include_routers(...)
    core/                     # ядро бота
      logs.py                 # logging → files/logs.txt + stdout
      user.py                 # class User { API }
      states.py               # get_user_status/delete_user_status (users_states, user_auths)
      pages.py                # Pages / Keyboard_pages + messages_pages dict
      pages_callbacks.py      # turn_left/turn_right
      keyboards.py            # make_return_keyboard etc.
      returns.py              # return_* callbacks
      start.py                # /start, generate_start_message
      journal_500.py          # get_500_message
    auth/
      authorization_callbacks.py  # Auth_states, init_auth/logout
      auth_funcs.py           # @check_auth, @load_user (lazy-загрузка из БД)
    main_functions/
      profile/                # профиль, статистика
      schedule.py             # расписание (в т.ч. "ОКНО" между парами)
      homework/               # get/send/delete_homework (+ пагинация по 6/7)
      marks/                  # marks.py, generate_html_marks.py, upload.py (FastAPI)
    some_funcs/               # "Разное"
      menu.py                 # агрегатор разное-меню
      activity.py / leaderboards.py / feedbacks.py / market.py / exams.py / rate_all_lessons.py
      settings/               # settings.py, timezone, get_homework_notifications, get_broadcast
    admin/
      admin.py                # /skibidi_admin (DEV-only)
      admin_funcs.py          # check_on_dev
      broadcast.py            # рассылка
    notifications/
      notifications_main.py   # init_notifications → scheduler.start()
      almost_expired_homework.py  # cron 59-я минута каждого часа
    about.py                  # "О боте"
```

## Переменные окружения
Только из env, никогда не хардкодить (см. глобальные правила). Требуются:
- `BOT_TOKEN` — токен от BotFather
- `POSTGRES_PASSWORD`, `POSTGRES_DB` (`POSTGRES_DB_NAME` в `.env_example`)
- `DEV_TELEGRAM_ID` — доступ к `/skibidi_admin`
- `MARKS_DOMAIN`, `MARKS_ENDPOINT` — для `upload.py` (формирует `https://{MARKS_DOMAIN}/{MARKS_ENDPOINT}/{uuid}.html`)
- `SUPPORT_USERNAME=igor_ppk_help_bot` — захардкожен в `storage.py` (исключение)
- `TZ=Asia/Krasnoyarsk` — в Dockerfile

`.env` не коммитить, `.env_example` — шаблон. `.gitignore` уже содержит `.env`.

## База данных
Два класса в `src/db/Journal_database.py`, оба `create_async_engine(f"postgresql+asyncpg://postgres:{PASSWORD}@postgres_db/{DB_NAME}")`:

- `Creds_db` → `Users(id, telegram_id BIGINT, username VARCHAR(30), password VARCHAR(100), JWT_token TEXT)`
- `Settings_db` → `user_settings(id, telegram_id BIGINT UNIQUE, settings JSONB DEFAULT '{"get_almost_expired_hw_notifications": true, "get_admin_broadcasts": true}')`, по факту `{"get_almost_expired_hw_notifications", "get_admin_broadcasts", "timezone": "0"}`

Все SQL — только параметризованные (`sqlalchemy.text` + `dict`), конкатенация запрещена. `jsonb_set` через `CAST(:value AS jsonb)`, путь как `text[]`.

## API-слой (`src/api/Journal_API.py`)
- `API_HOST=msapi.top-academy.ru`, `application_key=6a56a5df...` захардкожен
- `API(USER, PASS, JWT_token)` → `init_user()` → `update_JWT_headers()` → `get_JWT_token()` (POST `/api/v2/auth/login`)
- `__send_get_request` / `__send_post_request` — retry 3, `__status_code_checker` (200-299 иначе Exception), `__exception_handler` (422/401/403 → refresh JWT)
- Методы: `get_schedule_by_date`, `get_homework(status, page)`, `get_homework_count`, `get_user_info`, `send_homework`, `delete_homework`, `get_marks`, `get_lessons_for_feedback`, `send_lesson_feedback`, `get_student_feedbacks`, `get_market_products`, `get_leader_tables_stats`, `get_leaderboard_group/stream`, `get_activity`, `get_future_exams`, `get_student_visits_procent`

## Хранилища в памяти (`src/storage.py`)
```python
users_states: dict[int, User]       # FSM-состояния (states.py)
user_auths: dict[int, {User_obj}]   # авторизованные API-объекты
homework_pages_data: dict
settings_pages: dict
messages_pages: dict[int, dict[msg_id, Pages]]  # в pages.py
notification_scheduler = AsyncIOScheduler(timezone="Asia/Krasnoyarsk")
```
Все — глобальные dict, не потокобезопасны, живут в одном процессе. `check_auth` лениво восстанавливает из БД, `load_user` (для уведомлений) грузит/выгружает.

## Роутеры (aiogram)
- `bot_main.py` собирает `core_routers` (auth, start, return, pages) + `main_routers` (schedule, profile, homework, marks) + `some_menu_router`, `admin_router`, `about_router` → `dp.include_routers(...)`
- Каждый модуль экспортирует `Router` (напр. `homework_router`, `marks_router`, `admin_router`). Новые фичи — добавлять Router и регистрировать в `bot_main.py`
- Декораторы: `@check_auth` на все защищённые хендлеры, `@check_on_dev` на админку

## Пагинация (`src/bot/core/pages.py`)
`Pages` (текст) и `Keyboard_pages` (inline-клавиатура). `add_page`/`turn_left/right`, `add_debug_page` — ленивая догрузка следующей страницы ДЗ. `messages_pages[telegram_id][message_id]` хранит объект страниц для `pages_callbacks.py`.

## Уведомления
`APScheduler` задача `almost_exp_notification`: `CronTrigger(hour='*', minute=59)` → `check_homework_start` → перебор всех `telegram_id` из БД → `check_homework` (проверка `get_homework_count`/`get_homework(type=3)`, расчёт `deadline - today + timezone поправка`, окна `17ч / 1.5д / 6ч`). Уважает `settings.get_almost_expired_hw_notifications`. Игнор `TelegramForbiddenError` → удаление настроек.

## Marks / Upload (FastAPI)
`src/bot/main_functions/marks/upload.py`: `POST /upload` (требует `X-Auth-Token: broodskoye` + IP `127.0.0.1`), принимает `.html/.txt`, сохраняет в `uploads/{uuid}.html`, отдаёт `https://{MARKS_DOMAIN}/{MARKS_ENDPOINT}/{uuid}.html`, автоудаление через 600с (`BackgroundTasks`). Статика: `app.mount("/{MARKS_ENDPOINT}", StaticFiles(directory=UPLOAD_DIR))`. Порт `8000` проброшен в `docker-compose.yml`.

## Запуск
```bash
cp .env_example .env  # заполнить BOT_TOKEN, POSTGRES_*, DEV_TELEGRAM_ID, MARKS_*
docker compose up -d                # dev (polling, единственный режим сейчас)
docker compose --profile prod up -d # описан в README, но compose.yml сейчас без profiles
# локально без Docker:
pip install -r requirements.txt
python main.py  # требует запущенный postgres_db и env
```
`README` упоминает `BOT_ENV=dev/prod`, `WEBHOOK_DOMAIN/ENDPOINT`, `certs/`, `nginx` — в текущем `docker-compose.yml`/`main.py` не реализовано (только polling). Не использовать как референс для деплоя.

## Логи
`src/bot/core/logs.py`: `logging.basicConfig` → `files/logs.txt` + `StreamHandler`. Использовать `logger.info/warning/error`, не `print()` (в `almost_expired_homework.py` остались `print` — техдолг). Токены/пароли в логи не писать.

## Правила для агента
- Даты — из БД/API, не хардкодить
- Секреты — только `os.getenv`, не в коде/репозитории
- SQL — только параметризованный (`sqlalchemy.text` + dict)
- Python: type hints на публичном API, `logging`/`structlog` вместо `print`, `except: pass` запрещён, `assert` не для валидации, без `eval`/`exec`/`pickle.loads`
- `.gitignore`: `.env*`, `*.pem`, `id_*`
- Не рефакторить без просьбы; новую зависимость — согласовывать
- Перед правкой >10 строк — показать diff; не удалять/перезаписывать без подтверждения
- Если несколько решений — предложить, спросить какой выбрать

## Планы и ретро (глобальные правила)
- План фичи → `plans/YYYY-MM-DD-название.md`, фазы `[ ]/[x]`, проверка реализуемости (доки/версии)
- Цикл: Исследование → План → Challenge → Реализация по фазам (триггер "Implement Phase N") → Ревью 10 причин → Коммит+деплой
- После фичи → `retrospectives/YYYY-MM-DD-что-сделали.md`

## Готchas / Техдолг
- `main.py` использует `asyncio.gather(start_api(), start_bot())` — `start_api()` блокирует (`await server.serve()`), порядок важен; оба должны быть в одном event loop
- `upload.py`: `API_TOKEN` захардкожен, `ALLOWED_IPS` только `127.0.0.1` — не для prod
- `Journal_API.__exception_handler` содержит `return` без кода после `update_JWT_headers()` и закомментированный `logout` — retry может вернуть `None`
- `get_homework`/`get_marks` дублируют `json.loads` и проверки `None/[]` → возврат `False` смешивается с `dict/list`
- In-memory dict (`user_auths` etc.) теряются при рестарте, не масштабируются
- Нет тестов/линтера/mypy в репозитории; `requirements.txt` без пинов версий
- `.git_old/` вместо `.git/` — репозиторий не инициализирован как git (коммиты через `.git_old` не работают без переименования)
- `files/`/`uploads/` создаются в рантайме, должны быть в `.dockerignore`/`.gitignore` и volume
- `docker-compose.yml` пробрасывает `8000:8000` наружу — для prod нужен reverse proxy
