from datetime import UTC, datetime

from src.shared.exceptions.domain_exceptions import BusinessRuleValidationException


def normalize_date_range(
    date_from: datetime | None, date_to: datetime | None
) -> tuple[datetime | None, datetime | None]:
    """Normaliza a UTC y aplica intervalo semiabierto [date_from, date_to)."""
    for value in (date_from, date_to):
        if value is not None and value.tzinfo is None:
            raise BusinessRuleValidationException(
                "Las fechas deben incluir zona horaria, por ejemplo Z o +00:00"
            )
    normalized_from = date_from.astimezone(UTC) if date_from else None
    normalized_to = date_to.astimezone(UTC) if date_to else None
    if normalized_from and normalized_to and normalized_from >= normalized_to:
        raise BusinessRuleValidationException(
            "date_from debe ser anterior a date_to; el límite final es exclusivo"
        )
    return normalized_from, normalized_to
