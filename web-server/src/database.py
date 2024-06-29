import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        db_path = os.getenv('DATABASE_PATH')
        if not db_path:
            raise ValueError("DATABASE_PATH not set in environment variables")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    # Метод для добавления события
    def add_event(self, title, description, category, event_time):
        self.cursor.execute('''
        INSERT INTO events (title, description, category, event_time)
        VALUES (?, ?, ?, ?)
        ''', (title, description, category, event_time))
        self.conn.commit()

    # Метод для добавления подписчика в телеге
    def add_telegram_subscriber(self, telegram_id, category):
        self.cursor.execute('''
        INSERT INTO telegram_subscribers (id, category)
        VALUES (?, ?)
        ''', (telegram_id, category))
        self.conn.commit()

    # Метод для добавления email-подписчика
    def add_email_subscriber(self, email, category):
        self.cursor.execute('''
        INSERT INTO email_subscribers (email, category)
        VALUES (?, ?)
        ''', (email, category))
        self.conn.commit()
