from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)


def build_page(items: list[T], total: int, page: int, page_size: int) -> Page[T]:
    pages = (total + page_size - 1) // page_size
    return Page(items=items, total=total, page=page, page_size=page_size, pages=pages)
