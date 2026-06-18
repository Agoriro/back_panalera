# Paso 14: src/application/dtos/user_dto.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    user: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    id_role: UUID

class UserUpdate(BaseModel):
    user: Optional[str] = Field(None, min_length=3, max_length=50)
    id_role: Optional[UUID] = None

class UserResponse(BaseModel):
    id_user: UUID
    user: str
    id_role: UUID
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
