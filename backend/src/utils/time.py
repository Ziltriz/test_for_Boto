from datetime import datetime, timezone
from typing import Optional


def ms_to_datetime(ms: Optional[int]) -> Optional[datetime]:
    """Конвертация миллисекунды в  datetime для сервера приложения"""
    if ms is None or ms == 0:
        return None
    return datetime.fromtimestamp(int(ms) / 1000.0, tz=timezone.utc)


def dt_to_ms(dt: Optional[datetime]) -> Optional[int]:
    """Конвертация datetime в миллисекунды для мобильного приложения"""
    if dt is None:
        return None
    return int(dt.timestamp() * 1000)
