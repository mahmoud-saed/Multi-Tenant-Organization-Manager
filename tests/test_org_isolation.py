import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, login_user, register_user


async def _create_two_orgs(client: AsyncClient):
    """Create two separate orgs with separate admins, return (org1_id, token1, org2_id, token2)."""
    await register_user(client, "iso_admin1@example.com", "Pass123", "Iso Admin 1")
    token1 = await login_user(client, "iso_admin1@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "Iso Org 1"},
        headers=auth_header(token1),
    )
    org1_id = resp.json()["org_id"]

    await register_user(client, "iso_admin2@example.com", "Pass123", "Iso Admin 2")
    token2 = await login_user(client, "iso_admin2@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "Iso Org 2"},
        headers=auth_header(token2),
    )
    org2_id = resp.json()["org_id"]

    return org1_id, token1, org2_id, token2


@pytest.mark.asyncio
async def test_user_cannot_access_other_org_items(client: AsyncClient):
    org1_id, token1, org2_id, token2 = await _create_two_orgs(client)

    await client.post(
        f"/organizations/{org1_id}/items",
        json={"item_details": {"name": "Item in Org 1"}},
        headers=auth_header(token1),
    )

    resp = await client.get(
        f"/organizations/{org1_id}/items",
        headers=auth_header(token2),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_access_other_org_audit_logs(client: AsyncClient):
    org1_id, token1, org2_id, token2 = await _create_two_orgs(client)

    resp = await client.get(
        f"/organizations/{org1_id}/audit-logs",
        headers=auth_header(token2),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_member_sees_only_own_items(client: AsyncClient):
    await register_user(client, "own_admin@example.com", "Pass123", "Own Admin")
    admin_token = await login_user(client, "own_admin@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "Own Items Org"},
        headers=auth_header(admin_token),
    )
    org_id = resp.json()["org_id"]

    await client.post(
        f"/organizations/{org_id}/items",
        json={"item_details": {"name": "Admin Item"}},
        headers=auth_header(admin_token),
    )

    await register_user(client, "own_member@example.com", "Pass123", "Own Member")
    member_token = await login_user(client, "own_member@example.com", "Pass123")

    await client.post(
        f"/organizations/{org_id}/users",
        json={"email": "own_member@example.com", "role": "member"},
        headers=auth_header(admin_token),
    )

    await client.post(
        f"/organizations/{org_id}/items",
        json={"item_details": {"name": "Member Item"}},
        headers=auth_header(member_token),
    )

    resp = await client.get(
        f"/organizations/{org_id}/items",
        headers=auth_header(member_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["details"]["name"] == "Member Item"
