import os
from src.db.Journal_database import Creds_db

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ENV = os.getenv("BOT_ENV")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT")

db_obj = Creds_db()
users_states = {} # Состояния пользователей
user_auths = {} # Авторизированные пользователи