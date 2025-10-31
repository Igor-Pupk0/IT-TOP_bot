import sqlite3

DB_PATH = "files/creds.db"

class Creds_db:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        JWT_token TEXT NOT NULL                    
        )
        """)
        self.connection.commit()
        self.connection.close()

    def insert_user_creds(self, telegram_id: int, username: str, password: str):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute('INSERT INTO Users (telegram_id, username, password, JWT_token) VALUES (?, ?, ?, ?)', (telegram_id, username, password, "None"))
        self.connection.commit()
        self.connection.close()

    def update_user_data(self, telegram_id: int, username: str, password: str):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute("UPDATE Users SET username = ?, password = ? WHERE telegram_id = ?", (username, password, telegram_id))
        self.connection.commit()
        self.connection.close()

    def update_user_JWT_token(self, username: str, JWT_token: str):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute("UPDATE Users SET JWT_token = ? WHERE username = ?", (JWT_token, username))
        self.connection.commit()
        self.connection.close()

    def get_all_by_telegram_id(self, telegram_id: int):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT username, password, JWT_token FROM Users WHERE telegram_id = ?", (telegram_id,))
        user_data = self.cursor.fetchone()
        self.connection.close()
        return user_data
    
    def delete_user_by_telegram_id(self, telegram_id: int):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute("DELETE FROM Users WHERE telegram_id = ?", (telegram_id,))
        self.connection.commit()
        self.connection.close()

    def get_all_telegram_ids(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT telegram_id FROM Users")
        user_data = self.cursor.fetchall()
        self.connection.close()
        return user_data

    def get_telegram_id_by_JWT_token(self, JWT_TOKEN: str):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT telegram_id FROM Users WHERE JWT_token = ?", (JWT_TOKEN,))
        user_data = self.cursor.fetchone()
        self.connection.close()
        return user_data