from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from src.application.dtos.auth_dto import LoginRequest, RefreshRequest
from src.application.use_cases.auth_use_case import AuthUseCase
from src.domain.entities.user import User
from src.infrastructure.security.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from src.infrastructure.security.password import get_password_hash
from src.interfaces.api.dependencies.auth import is_authenticated
from src.shared.exceptions.domain_exceptions import UnauthorizedException


def make_user(*, active: bool = True, role: str = "Admin", version: int = 0) -> User:
    return User(
        id_user=uuid4(),
        user="admin",
        password="unused-hash",
        id_role=uuid4(),
        is_active=active,
        token_version=version,
        role_name=role,
    )


def test_access_and_refresh_tokens_are_not_interchangeable():
    subject = str(uuid4())
    access_token = create_access_token({"sub": subject})
    refresh_token = create_refresh_token({"sub": subject, "ver": 0})

    assert verify_token(access_token, "access")["type"] == "access"
    assert verify_token(refresh_token, "refresh")["type"] == "refresh"

    with pytest.raises(UnauthorizedException):
        verify_token(access_token, "refresh")
    with pytest.raises(UnauthorizedException):
        verify_token(refresh_token, "access")


@pytest.mark.asyncio
async def test_login_issues_typed_tokens_with_current_version():
    user = make_user(version=7)
    user.password = get_password_hash("valid-password")
    user_repo = AsyncMock()
    user_repo.get_by_username.return_value = user

    response = await AuthUseCase(user_repo).login(
        LoginRequest(username=user.user, password="valid-password")
    )

    assert verify_token(response.access_token, "access")["sub"] == str(user.id_user)
    refresh_payload = verify_token(response.refresh_token, "refresh")
    assert refresh_payload["ver"] == 7


@pytest.mark.asyncio
async def test_refresh_rotates_once_and_rejects_reuse():
    original_user = make_user(version=0)
    rotated_user = make_user(version=1)
    rotated_user.id_user = original_user.id_user
    user_repo = AsyncMock()
    user_repo.rotate_token_version.side_effect = [rotated_user, None]
    use_case = AuthUseCase(user_repo)
    original_refresh = create_refresh_token(
        {"sub": str(original_user.id_user), "ver": 0}
    )
    request = RefreshRequest(refresh_token=original_refresh)

    response = await use_case.refresh(request)

    assert response.refresh_token != original_refresh
    assert verify_token(response.refresh_token, "refresh")["ver"] == 1
    with pytest.raises(UnauthorizedException):
        await use_case.refresh(request)


@pytest.mark.asyncio
async def test_authentication_uses_current_user_role():
    user = make_user(role="Operator")
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = user
    token = create_access_token({"sub": str(user.id_user), "role": "Admin"})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    payload = await is_authenticated(credentials, user_repo)

    assert payload["role"] == "Operator"


@pytest.mark.asyncio
async def test_inactive_user_cannot_use_valid_access_token():
    user = make_user(active=False)
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = user
    token = create_access_token({"sub": str(user.id_user)})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(UnauthorizedException):
        await is_authenticated(credentials, user_repo)
