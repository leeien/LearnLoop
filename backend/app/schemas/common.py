from typing import Generic, TypeVar

from pydantic import BaseModel


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: DataT
    message: str
    cache_hit: bool | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    message: str
