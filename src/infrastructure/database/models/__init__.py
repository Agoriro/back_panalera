# Paso 10: src/infrastructure/database/models/__init__.py
"""
Exportación de todos los modelos para que Alembic pueda detectarlos.
"""

from src.infrastructure.database.models.base import Base
from src.infrastructure.database.models.catalog import (
    CategoryModel,
    ColorModel,
    GenderModel,
    SizeModel,
    SupplierModel,
)
from src.infrastructure.database.models.inventory import (
    InventoryModel,
    InventoryPhotoModel,
)
from src.infrastructure.database.models.movement import MovementModel
from src.infrastructure.database.models.role import RoleModel
from src.infrastructure.database.models.user import UserModel

__all__ = [
    "Base",
    "RoleModel",
    "UserModel",
    "SupplierModel",
    "ColorModel",
    "SizeModel",
    "CategoryModel",
    "GenderModel",
    "InventoryModel",
    "InventoryPhotoModel",
    "MovementModel",
]
