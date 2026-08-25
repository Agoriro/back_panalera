"""Traducción de errores de integridad de base de datos al dominio."""

from sqlalchemy.exc import IntegrityError

from src.shared.exceptions.domain_exceptions import (
    BusinessRuleValidationException,
    ResourceAlreadyExistsException,
)


def translate_integrity_error(exc: IntegrityError) -> Exception:
    """Convierte violaciones conocidas sin exponer detalles internos de la DB."""
    original = exc.orig
    sqlstate = getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)
    message = str(original).lower()

    if sqlstate == "23505" or "unique constraint failed" in message:
        if "barcode" in message:
            return ResourceAlreadyExistsException("El código de barras ya existe")
        if "code_inventory" in message or "uq_inventory_code" in message:
            return ResourceAlreadyExistsException("El SKU ya existe")
        return ResourceAlreadyExistsException("El recurso ya existe")

    if sqlstate == "23503" or "foreign key constraint failed" in message:
        return BusinessRuleValidationException("La relación indicada no existe")

    if sqlstate == "23514" or "check constraint failed" in message:
        return BusinessRuleValidationException(
            "Los datos violan una regla de integridad"
        )

    return BusinessRuleValidationException("No fue posible guardar los datos")
