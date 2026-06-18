# Paso 14: src/application/dtos/role_dto.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class RoleUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class RoleResponse(BaseModel):
    id_role: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)
