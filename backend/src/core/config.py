from typing import Any, List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    CLIENT_ID: str = Field(default="", validation_alias="CLIENT_ID")
    CLIENT_SECRET: str = Field(default="", validation_alias="CLIENT_SECRET")

    VERSION: str = Field(default="0.1.0", validation_alias="VERSION")
    DEBUG: bool = Field(default=True, validation_alias="DEBUG")

    DB_PATH: str = Field(default="boto.db", validation_alias="DB_PATH")

    WEB_CONCURRENCY: int = Field(default=9, validation_alias="WEB_CONCURRENCY")
    MAX_OVERFLOW: int = Field(default=64, validation_alias="MAX_OVERFLOW")

    SENDER_GMAIL: str = Field(default="example@gmail.com", validation_alias="SENDER_GMAIL")
    SENDER_GMAIL_PASSWORD: str = Field(default="211231", validation_alias="SENDER_GMAIL_PASSWORD")

    POOL_SIZE: Optional[int] = None
    POSTGRES_URL: Optional[str] = None

    SECRET_KEY: str = Field(default="", validation_alias="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", validation_alias="ALGORITHM")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",           
    )

    @field_validator("POOL_SIZE", mode="before")
    @classmethod
    def build_pool(cls, v: Optional[Any], info: ValidationInfo) -> int:
        if isinstance(v, int):
            return v

        db_pool = info.data.get("DB_POOL_SIZE", 83)
        web_conc = info.data.get("WEB_CONCURRENCY", 9)
        return max(db_pool // web_conc, 5)


settings = Settings()