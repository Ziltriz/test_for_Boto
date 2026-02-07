import uuid as uuid_pkg
from sqlalchemy import event
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel


class BaseModel(SQLModel):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    )


@event.listens_for(BaseModel, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    """Автоматически обновляет updated_at при изменении записи"""
    target.updated_at = datetime.now(timezone.utc)
