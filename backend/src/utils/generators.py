import random
import string
from fastapi import Request

BASE62 = string.digits + string.ascii_letters


def generate_short_code() -> str:
    length = random.randint(4, 8)
    return "".join(random.choices(BASE62, k=length))


def get_base_url(request: Request) -> str:
    """
    Возвращает базовый URL без пути и query-параметров.
    Пример:
    - http://localhost:8000
    """
    scheme = request.url.scheme         
    host = request.url.netloc           
    
    return f"{scheme}://{host}"