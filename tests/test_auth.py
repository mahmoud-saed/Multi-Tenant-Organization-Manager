import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, login_user, register_user


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/auth/register",
        json={
            "email": "auth_test@example.com",
            "password": "StrongPassword123",
            "full_name": "Auth Test",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "user_id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    email = "dup_test@example.com"
    await register_user(client, email, "Pass123", "Dup User")
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": "Pass123", "full_name": "Dup User 2"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    email = "login_test@example.com"
    await register_user(client, email, "Pass123", "Login User")
    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": "Pass123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    email = "wrong_pw@example.com"
    await register_user(client, email, "CorrectPass", "Wrong PW User")
    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": "WrongPass"},
    )
    assert resp.status_code == 401
