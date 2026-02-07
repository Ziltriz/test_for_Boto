from typing import TypeVar, Optional, Dict, Any, List

from src.db.session import get_db

from src.db.base_client import AbstractDbClient
from src.schemas.common import UrlInfo
from src.core.config import settings

T = TypeVar("T")
db_path = settings.DB_PATH

class UrlInfoDbClient(AbstractDbClient[Dict[str, Any], UrlInfo]):
    """
    Клиент для работы со станциями в PostgreSQL.
    """


    table_name = "urls"
    schema: UrlInfo = UrlInfo


    @classmethod
    def get_by_id(cls, original_url: str, short_code: str = None) -> Optional[UrlInfo]:
        """Получить запись об сокращенной ссылки по коду"""
        with get_db(db_path) as session:
            if not short_code:

                cursor = session.execute(
                    """
                    SELECT short_url, original_url, short_code, created_at, clicks 
                    FROM urls
                    WHERE original_url = ?
                    """,
                    (original_url,)
                )
            else:
                cursor = session.execute(
                    """
                    SELECT short_url, original_url, short_code, created_at, clicks 
                    FROM urls
                    WHERE short_code = ?
                    """,
                    (short_code,)
                )
            row = cursor.fetchone()
            if row:
                return cls.schema.model_validate(dict(row))
    

    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[UrlInfo | None ]:
        """Получить все сокращенные ссылки """
        with get_db(db_path) as session:
            cursor = session.execute(
                """
                SELECT short_url, original_url, short_code, created_at, clicks
                FROM urls
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, skip)
            )

            rows = cursor.fetchall()

            return [cls.schema.model_validate(dict(row) for row in rows)]
            
    @classmethod
    def delete_by_id(cls, original_url: str) -> bool:
        """Удлаить сокращенную ссылку по полной ссылке"""
        with get_db(db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM urls WHERE original_url = ?",
                (original_url,)
            )
            conn.commit()
            return cursor.rowcount > 0
        
    @classmethod
    def process(cls, data: Dict[str, Any]) -> UrlInfo:
        """
        Создать или обновить сокращенную ссылку и
        data должен содержать как минимум:
        short_code, original_url
        """
        required = {"short_url", "original_url", "short_code"}
        if not required.issubset(data.keys()):
            raise ValueError(f"Пропущены обязательные поля: {required - set(data.keys())}")

        with get_db(db_path) as session:
            session.execute(
                """
                INSERT OR REPLACE INTO urls
                (short_url, original_url, short_code, created_at, clicks)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
                """,
                (
                    data.get('short_url'),
                    data.get('original_url'),
                    data.get('short_code'),
                    data.get('clicks')
                )
            )
            session.commit()
        
        row = cls.get_by_id(data.get('short_url'))
        if row:
            raise RuntimeError("Ошибка создания или обновления ссылки")



    @classmethod
    def increment_clicks(cls, original_url: str) -> Optional[UrlInfo]:
        """Получить запись об сокращенной ссылки по коду"""
        with get_db(db_path) as session:
            cursor = session.execute(
                """
                UPDATE urls
                SET clicks = clicks + 1
                WHERE original_url = ?
                """,
                (original_url, )
            )
            session.commit()
            return cursor.rowcount > 0