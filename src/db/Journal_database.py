import sqlalchemy
from sqlalchemy.orm.session import Session
import os

USERNAME = 'postgres'
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")

class Creds_db:
    def __init__(self):
        self.engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@postgres_db/{DB_NAME}")

        with Session(self.engine) as session:

            session.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS Users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            username VARCHAR(30) NOT NULL,
            password VARCHAR(100) NOT NULL,
            JWT_token TEXT NOT NULL
            )
            """))
            session.commit()

    def insert_user_creds(self, telegram_id: int, username: str, password: str):
        with Session(self.engine) as session:
            session.execute(sqlalchemy.text('INSERT INTO Users (telegram_id, username, password, JWT_token) VALUES (:telegram_id, :username, :password, :JWT_token)'), {"telegram_id": telegram_id, "username": username, "password": password, "JWT_token": "None"})
            session.commit()

    def update_user_data(self, telegram_id: int, username: str, password: str):
        with Session(self.engine) as session:
            session.execute(sqlalchemy.text("UPDATE Users SET username = :username, password = :password WHERE telegram_id = :telegram_id"), {"telegram_id": telegram_id, "username": username, "password": password})
            session.commit()

    def update_user_JWT_token(self, username: str, JWT_token: str):
        with Session(self.engine) as session:
            session.execute(sqlalchemy.text("UPDATE Users SET JWT_token = :JWT_token WHERE username = :username"), {"username": username, "JWT_token": "None"})
            session.commit()

    def get_all_by_telegram_id(self, telegram_id: int):
        with Session(self.engine) as session:
            result = session.execute(sqlalchemy.text("SELECT username, password, JWT_token FROM Users WHERE telegram_id = :telegram_id"), {"telegram_id": telegram_id})
            
        return result.fetchone()
    
    def delete_user_by_telegram_id(self, telegram_id: int):
        with Session(self.engine) as session:
            session.execute(sqlalchemy.text("DELETE FROM Users WHERE telegram_id = :telegram_id"), {"telegram_id": telegram_id})
            session.commit()

    def get_all_telegram_ids(self):
        with Session(self.engine) as session:
            result = session.execute(sqlalchemy.text("SELECT telegram_id FROM Users"))

        return result.fetchall()

    def get_telegram_id_by_user(self, username: str):
        with Session(self.engine) as session:
            result = session.execute(sqlalchemy.text("SELECT telegram_id FROM Users WHERE username = :username"), {"username": username})

        return result.fetchone()
    
class Settings_db:
    def __init__(self):
        self.engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@postgres_db/{DB_NAME}")

        with Session(self.engine) as session:

            session.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            get_almost_expired_hw_notifictions BOOLEAN NOT NULL DEFAULT TRUE,
            get_admin_brodcasts BOOLEAN NOT NULL DEFAULT TRUE
            )
            """))
            session.commit()

    def init_user_settings(self, telegram_id: int):
        with Session(self.engine) as session:
            session.execute(sqlalchemy.text('INSERT INTO user_settings (telegram_id) VALUES (:telegram_id)'), {"telegram_id": telegram_id})
            session.commit()

    def update_user_settings(self, telegram_id: int, parametr: str, value: str):
        with Session(self.engine) as session:
            session.execute(sqlalchemy.text(f"UPDATE user_settings SET {parametr} = :value WHERE telegram_id = :telegram_id"), {"value": value, "telegram_id": telegram_id})
            session.commit()

    def get_all_settings_by_telegram_id(self, telegram_id: int):
        with Session(self.engine) as session:
            result = session.execute(sqlalchemy.text("SELECT * FROM user_settings WHERE telegram_id = :telegram_id"), {"telegram_id": telegram_id}).fetchone()
            session.commit()

        try:
            return dict(result._mapping)
        except:
            return 

    def delete_settings_by_telegram_id(self, telegram_id: int):
        with Session(self.engine) as session:
            session.execute(sqlalchemy.text("DELETE FROM user_settings WHERE telegram_id = :telegram_id", {"telegram_id": telegram_id}))
            session.commit()
