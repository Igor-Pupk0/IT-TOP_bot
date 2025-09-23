import json
from src.db.Journal_database import Creds_db

CONFIG_PATH = "files/config.json"

with open(CONFIG_PATH) as file:
    TOKEN = json.loads(file.read())["BOT_TOKEN"]


db_obj = Creds_db()
users_states = {} # Состояния пользователей
user_auths = {} # Авторизированные пользователи