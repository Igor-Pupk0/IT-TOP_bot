import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
import json

USERNAME = 'postgres'
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")

class Creds_db:
    def __init__(self):
        self.engine = create_async_engine(f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@postgres_db/{DB_NAME}")

        self.session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def __execute_and_commite(self, text: sqlalchemy.TextClause, data: dict = {}):
        async with self.engine.begin() as conn:
            await conn.execute(text, data)

    async def init_db(self):
        await self.__execute_and_commite(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS Users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            username VARCHAR(30) NOT NULL,
            password VARCHAR(100) NOT NULL,
            JWT_token TEXT NOT NULL
            )
            """))

    async def insert_user_creds(self, telegram_id: int, username: str, password: str):
        await self.__execute_and_commite(
            sqlalchemy.text(
                'INSERT INTO Users (telegram_id, username, password, JWT_token) VALUES (:telegram_id, :username, :password, :JWT_token)'), 
                {"telegram_id": telegram_id, "username": username, "password": password, "JWT_token": "None"}
            )

    async def update_user_data(self, telegram_id: int, username: str, password: str):
        await self.__execute_and_commite(
            sqlalchemy.text("UPDATE Users SET username = :username, password = :password WHERE telegram_id = :telegram_id"), 
            {"telegram_id": telegram_id, "username": username, "password": password}
        )

    async def update_user_JWT_token(self, username: str, JWT_token: str):
        await self.__execute_and_commite(
            sqlalchemy.text("UPDATE Users SET JWT_token = :JWT_token WHERE username = :username"), 
            {"username": username, "JWT_token": JWT_token}
        )


    async def get_all_by_telegram_id(self, telegram_id: int):
        async with self.engine.begin() as connection:
            result = await connection.execute(
                sqlalchemy.text("SELECT username, password, JWT_token FROM Users WHERE telegram_id = :telegram_id"), 
                {"telegram_id": telegram_id}
            )
            
        return result.fetchone()
    
    async def delete_user_by_telegram_id(self, telegram_id: int):
        await self.__execute_and_commite(
            sqlalchemy.text("DELETE FROM Users WHERE telegram_id = :telegram_id"), 
            {"telegram_id": telegram_id}
        )


    async def get_all_telegram_ids(self):
        async with self.engine.begin() as connection:
            result = await connection.execute(sqlalchemy.text("SELECT telegram_id FROM Users"))

        return result.fetchall()

    async def get_telegram_id_by_user(self, username: str):
        async with self.engine.begin() as connection:
            result = await connection.execute(
                sqlalchemy.text("SELECT telegram_id FROM Users WHERE username = :username"), 
                {"username": username}
            )

        return result.fetchone()
    

class Settings_db:
    def __init__(self):
        self.engine = create_async_engine(f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@postgres_db/{DB_NAME}")

    async def init_db(self):
        
        query = sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                settings JSONB DEFAULT '{"get_almost_expired_hw_notifications": true, "get_admin_broadcasts": true}'::jsonb
            )
        """)
        async with self.engine.begin() as conn:
            await conn.execute(query)

    async def init_user_settings(self, telegram_id: int):
        default_settings = {"get_almost_expired_hw_notifications": True, "get_admin_broadcasts": True, "timezone": "0"}
        query = sqlalchemy.text('INSERT INTO user_settings (telegram_id, settings) VALUES (:telegram_id, :settings)')
        async with self.engine.begin() as conn:
            await conn.execute(
                query, {
                        "telegram_id": telegram_id, 
                        "settings": json.dumps(default_settings)
                })

    async def update_user_settings(self, telegram_id: int, parametr: str, value: bool):
        # Используем стандартный CAST вместо "::", чтобы не путать парсер SQLAlchemy
        query = sqlalchemy.text("""
            UPDATE user_settings 
            SET settings = jsonb_set(settings, :path, CAST(:value AS jsonb)) 
            WHERE telegram_id = :telegram_id
        """)

        async with self.engine.begin() as conn:
            await conn.execute(query, {
                # Передаем как список ['имя_ключа'], asyncpg сам превратит его в text[]
                "path": [parametr], 
                "value": json.dumps(value),
                "telegram_id": telegram_id
            })

    async def get_all_settings_by_telegram_id(self, telegram_id: int):
        query = sqlalchemy.text("SELECT settings FROM user_settings WHERE telegram_id = :telegram_id")
        async with self.engine.begin() as conn:
            result = await conn.execute(query, {"telegram_id": telegram_id})
            row = result.fetchone()
            return row[0] if row else None

    async def delete_settings_by_telegram_id(self, telegram_id: int):
        query = sqlalchemy.text("DELETE FROM user_settings WHERE telegram_id = :telegram_id")
        
        async with self.engine.begin() as conn:
            await conn.execute(query, {"telegram_id": telegram_id})