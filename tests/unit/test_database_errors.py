from sqlalchemy.exc import IntegrityError

from src.infrastructure.database.errors import translate_integrity_error
from src.shared.exceptions.domain_exceptions import (
    BusinessRuleValidationException,
    ResourceAlreadyExistsException,
)


def test_translate_unique_integrity_error() -> None:
    error = IntegrityError(
        "INSERT", {}, Exception("UNIQUE constraint failed: inventory.code_inventory")
    )

    translated = translate_integrity_error(error)

    assert isinstance(translated, ResourceAlreadyExistsException)
    assert str(translated) == "El SKU ya existe"


def test_translate_foreign_key_integrity_error() -> None:
    error = IntegrityError("INSERT", {}, Exception("FOREIGN KEY constraint failed"))

    translated = translate_integrity_error(error)

    assert isinstance(translated, BusinessRuleValidationException)
    assert str(translated) == "La relación indicada no existe"
