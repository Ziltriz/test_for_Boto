from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Union, Any
import uuid as uuid_pkg
import json



class ShortenResponse(BaseModel):
    """
    Модель ответа для пользователя возвращает 
    """
    shorten_url: str = Field(
        ...,
        description="Короткая ссылка",
        example=["http://localhost:8000/abc123_byzil"]
    )
    code: str = Field(
        ...,
        description="Код после /",
        examples=["abcd_byzil"]
    )
    original_url: str = Field(
        ...,
        decription="Оригинальная ссылка как пришла"
    )


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None