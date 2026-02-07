import uuid as uuid_pkg
from pydantic import BaseModel, Field, HttpUrl, Field
from typing import Literal, List, Optional


class ShortenRequest(BaseModel):
    """
    Модель для запроса на сокращение ссылки
    """

    url: HttpUrl = Field(
        ...,
        description="Полная ссылка для сокращения", 
        example="https://example.com/very/long/path?query=param"
        )