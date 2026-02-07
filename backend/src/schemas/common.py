from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel
from datetime import datetime


DataType = TypeVar("DataType")


class IResponseBase(GenericModel, Generic[DataType]):
    message: str = ""
    meta: dict = {}
    data: Optional[DataType] = None


class IGetResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data got correctly"
    data: Optional[List[DataType]] = None


class IPostResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data created correctly"


class RawDocument(BaseModel):
    data: dict


class UrlInfo(BaseModel):
    short_url: str
    short_code: str
    original_url: str
    created_at: datetime | None = None
    clicks: int = 0

    class Config: 
        from_attributes = True