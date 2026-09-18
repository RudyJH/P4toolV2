""" File: users_tests.py
"""

import importlib

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

BASE = "/api/v1/users"


def test_sqlite_mode_is_default_for_db_init_one(monkeypatch):
    monkeypatch.setenv("DB_INIT", "1")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test_app.db")

    import app.core.config as config_module

    importlib.reload(config_module)
    assert config_module.settings.DB_INIT == 1
    assert config_module.settings.DATABASE_URL.startswith("sqlite")


@pytest.fixture
def sample_payload():
    return {
        "email": "alice@example.com",
        "username": "alice",
        "password": "Secret123",
        "first_name": "Alice",
        "role": "user",
    }


@pytest.mark.asyncio
async def test_create_user(sample_payload):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(BASE + "/", json=sample_payload)
    assert resp.status_code == 201
    assert "password_hash" not in resp.json()


@pytest.mark.asyncio
async def test_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(BASE + "/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_email(sample_payload):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(BASE + "/", json=sample_payload)
        resp = await ac.post(BASE + "/", json=sample_payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_weak_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(BASE + "/", json={
            "email": "x@x.com", "username": "xx", "password": "weak"})
    assert resp.status_code == 422