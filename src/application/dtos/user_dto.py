# Paso 14: src/application/dtos/user_dto.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    user: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    id_role: UUID


class UserUpdate(BaseModel):
    user: str | None = Field(None, min_length=3, max_length=50)
    id_role: UUID | None = None


class UserResponse(BaseModel):
    id_user: UUID
    user: str
    id_role: UUID
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
