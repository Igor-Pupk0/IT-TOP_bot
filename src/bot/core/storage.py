import os
import apscheduler.schedulers.background
from src.db.Journal_database import Creds_db, Settings_db

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")
ENV = os.getenv("BOT_ENV")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")
SUPPORT_USERNAME = "igor_ppk_help_bot"
DEV_TELEGRAM_ID = os.getenv("DEV_TELEGRAM_ID")

db_obj = Creds_db()
settings_db_obj = Settings_db()
users_states = {} # Состояния пользователей
user_auths = {} # Авторизированные пользователи
notification_scheduler = apscheduler.schedulers.background.BackgroundScheduler(timezone="Asia/Krasnoyarsk")