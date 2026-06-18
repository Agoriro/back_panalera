# Paso 9: src/domain/repositories/user_repository.py
"""
Interfaz de repositorio para la entidad User.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, id_user: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_all(self) -> List[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass
