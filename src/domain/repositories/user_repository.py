# Paso 9: src/domain/repositories/user_repository.py
"""
Interfaz de repositorio para la entidad User.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, id_user: UUID) -> User | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def rotate_token_version(
        self, id_user: UUID, expected_version: int
    ) -> User | None:
        """Incrementa versión solo si coincide, invalidando refresh token usado."""
        pass
