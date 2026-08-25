import pytest

from src.interfaces.api.dependencies.auth import Permission, has_permission
from src.shared.exceptions.domain_exceptions import ForbiddenException


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("role", "permission"),
    [
        ("Admin", Permission.MANAGE_USERS),
        ("Admin", Permission.MANAGE_CATALOG),
        ("Operator", Permission.WRITE_INVENTORY),
        ("Operator", Permission.WRITE_MOVEMENTS),
        ("Operator", Permission.READ_DATA),
        ("Consulta", Permission.READ_DATA),
    ],
)
async def test_role_has_expected_permission(role: str, permission: Permission):
    checker = has_permission(permission)

    assert await checker({"role": role}) is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("role", "permission"),
    [
        ("Operator", Permission.MANAGE_CATALOG),
        ("Operator", Permission.MANAGE_USERS),
        ("Consulta", Permission.WRITE_INVENTORY),
        ("Consulta", Permission.WRITE_MOVEMENTS),
        ("unknown", Permission.READ_DATA),
    ],
)
async def test_role_without_permission_is_forbidden(role: str, permission: Permission):
    checker = has_permission(permission)

    with pytest.raises(ForbiddenException):
        await checker({"role": role})
