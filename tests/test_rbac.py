import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, login_user, register_user


async def _setup_org_with_admin_and_member(client: AsyncClient):
    """Create an org with an admin and a member, return (org_id, admin_token, member_token)."""
    await register_user(client, "rbac_admin@example.com", "Pass123", "RBAC Admin")
    admin_token = await login_user(client, "rbac_admin@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "RBAC Test Org"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201
    org_id = resp.json()["org_id"]

    await register_user(client, "rbac_member@example.com", "Pass123", "RBAC Member")
    member_token = await login_user(client, "rbac_member@example.com", "Pass123")

    resp = await client.post(
        f"/organizations/{org_id}/users",
        json={"email": "rbac_member@example.com", "role": "member"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200

    return org_id, admin_token, member_token


@pytest.mark.asyncio
async def test_admin_can_invite_user(client: AsyncClient):
    await register_user(client, "invite_admin@example.com", "Pass123", "Invite Admin")
    admin_token = await login_user(client, "invite_admin@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "Invite Test Org"},
        headers=auth_header(admin_token),
    )
    org_id = resp.json()["org_id"]

    await register_user(client, "invitee@example.com", "Pass123", "Invitee")
    resp = await client.post(
        f"/organizations/{org_id}/users",
        json={"email": "invitee@example.com", "role": "member"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_member_cannot_invite_user(client: AsyncClient):
    org_id, admin_token, member_token = await _setup_org_with_admin_and_member(client)

    await register_user(client, "target_invitee@example.com", "Pass123", "Target")
    resp = await client.post(
        f"/organizations/{org_id}/users",
        json={"email": "target_invitee@example.com", "role": "member"},
        headers=auth_header(member_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_view_org_users(client: AsyncClient):
    await register_user(client, "view_admin@example.com", "Pass123", "View Admin")
    admin_token = await login_user(client, "view_admin@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "View Users Org"},
        headers=auth_header(admin_token),
    )
    org_id = resp.json()["org_id"]

    resp = await client.get(
        f"/organizations/{org_id}/users",
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_member_cannot_view_org_users(client: AsyncClient):
    await register_user(client, "viewu_admin@example.com", "Pass123", "VU Admin")
    admin_token = await login_user(client, "viewu_admin@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "VU Org"},
        headers=auth_header(admin_token),
    )
    org_id = resp.json()["org_id"]

    await register_user(client, "viewu_member@example.com", "Pass123", "VU Member")
    member_token = await login_user(client, "viewu_member@example.com", "Pass123")

    await client.post(
        f"/organizations/{org_id}/users",
        json={"email": "viewu_member@example.com", "role": "member"},
        headers=auth_header(admin_token),
    )

    resp = await client.get(
        f"/organizations/{org_id}/users",
        headers=auth_header(member_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_view_audit_logs(client: AsyncClient):
    await register_user(client, "audit_admin@example.com", "Pass123", "Audit Admin")
    admin_token = await login_user(client, "audit_admin@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "Audit Org"},
        headers=auth_header(admin_token),
    )
    org_id = resp.json()["org_id"]

    resp = await client.get(
        f"/organizations/{org_id}/audit-logs",
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_member_cannot_view_audit_logs(client: AsyncClient):
    await register_user(client, "auditm_admin@example.com", "Pass123", "AuditM Admin")
    admin_token = await login_user(client, "auditm_admin@example.com", "Pass123")

    resp = await client.post(
        "/organizations",
        json={"org_name": "AuditM Org"},
        headers=auth_header(admin_token),
    )
    org_id = resp.json()["org_id"]

    await register_user(client, "auditm_member@example.com", "Pass123", "AuditM Member")
    member_token = await login_user(client, "auditm_member@example.com", "Pass123")

    await client.post(
        f"/organizations/{org_id}/users",
        json={"email": "auditm_member@example.com", "role": "member"},
        headers=auth_header(admin_token),
    )

    resp = await client.get(
        f"/organizations/{org_id}/audit-logs",
        headers=auth_header(member_token),
    )
    assert resp.status_code == 403
