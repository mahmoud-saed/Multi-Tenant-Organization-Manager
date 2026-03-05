from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.organization import InviteRequest, OrgCreateRequest, OrgCreateResponse
from app.schemas.user import UserOut
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.post("", response_model=OrgCreateResponse, status_code=201)
async def create_organization(
    data: OrgCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await OrganizationService(db).create_org(user, data)


@router.post("/{org_id}/users")
async def invite_user(
    org_id: UUID,
    data: InviteRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await OrganizationService(db).invite_user(admin, org_id, data)


@router.get("/{org_id}/users", response_model=list[UserOut])
async def list_users(
    org_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await OrganizationService(db).list_users(org_id, limit, offset)


@router.get("/{org_id}/users/search", response_model=list[UserOut])
async def search_users(
    org_id: UUID,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await OrganizationService(db).search_users(org_id, q, limit, offset)
