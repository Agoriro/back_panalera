import pytest

from src.seed_db import seed_database
from src.shared.config.settings import settings


@pytest.mark.asyncio
async def test_seed_skips_admin_without_explicit_credentials(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BOOTSTRAP_ADMIN_USERNAME", None)
    monkeypatch.setattr(settings, "BOOTSTRAP_ADMIN_PASSWORD", None)

    await seed_database()

    assert "Bootstrap admin omitido" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_seed_rejects_partial_admin_credentials(monkeypatch):
    monkeypatch.setattr(settings, "BOOTSTRAP_ADMIN_USERNAME", "admin")
    monkeypatch.setattr(settings, "BOOTSTRAP_ADMIN_PASSWORD", None)

    with pytest.raises(RuntimeError, match="obligatorios juntos"):
        await seed_database()
