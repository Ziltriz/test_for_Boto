import sqlite3
from src.core.log_manager import LogManager
from src.core.config import settings
from contextlib import contextmanager



@contextmanager
def get_db(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        LogManager.sync_log_database_error("Соединенние с бд закрыто")
        conn.close()

async def on_startup():
    LogManager.sync_log_database_info("Инициализация базы данных")
    db_path = settings.DB_PATH
    with get_db(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                original_url TEXT PRIMARY KEY,
                short_code TEXT NOT NULL,
                short_url TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                clicks INT NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    LogManager.sync_log_database_info("Успех")