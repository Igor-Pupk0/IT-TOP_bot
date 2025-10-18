import os
from src.db.Journal_database import Creds_db

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ENV = os.getenv("BOT_ENV")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")
SUPPORT_USERNAME = "igor_ppk_help_bot"
DEV_TELEGRAM_ID = os.getenv("DEV_TELEGRAM_ID")

#
#   Notifications
#
ALMOST_EXPIRED_HOMEWORK_NOTIFICATION_TIMEOUT_SEC = 60 * 60



db_obj = Creds_db()
users_states = {} # Состояния пользователей
user_auths = {} # Авторизированные пользователи