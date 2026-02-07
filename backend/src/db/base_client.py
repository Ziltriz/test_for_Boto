from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")
M = TypeVar("M")


class AbstractDbClient(ABC, Generic[T, M]):
    """Абстрактный базовый класс для клиентов базы данных"""

    table_name: str
    schema: type[M]

    
    @classmethod
    @abstractmethod
    async def process(cls, data: T) -> M:
        """Основной метод для обработки и сохранения данных"""
        pass

    @classmethod
    @abstractmethod
    async def get_by_id(cls, id: int) -> Optional[M]:
        """Получить запись по ID"""
        pass

    @classmethod
    @abstractmethod
    async def get_existing_ids(cls) -> List[int]:
        """Получить список всех ID в базе"""
        pass
