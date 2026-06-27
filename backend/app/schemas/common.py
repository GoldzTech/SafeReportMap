from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


class MessageResponse(BaseModel):
    message: str


class IdResponse(BaseModel):
    id: UUID