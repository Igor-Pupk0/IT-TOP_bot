import aiogram
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.db.Journal_database import Creds_db, Settings_db

TOKEN = os.getenv("BOT_TOKEN")
MARKS_DOMAIN = os.getenv("MARKS_DOMAIN")
MARKS_ENDPOINT = os.getenv("MARKS_ENDPOINT")
SUPPORT_USERNAME = "igor_ppk_help_bot"
DEV_TELEGRAM_ID = os.getenv("DEV_TELEGRAM_ID")

bot = aiogram.Bot(TOKEN)
dp = aiogram.Dispatcher()
db_obj = Creds_db()
settings_db_obj = Settings_db()
users_states = {} # Состояния пользователей
user_auths = {} # Авторизированные пользователи
homework_pages_data = {} # Странички домашкних заданий
settings_pages = {}
failed_403_counts: dict[int, int] = {} # ponytail: RAM counter for 401/403/422, reset on success or restart
notification_scheduler = AsyncIOScheduler(timezone="Asia/Krasnoyarsk")