from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.org_repo import OrgRepository
from app.repositories.user_repo import UserRepository
from app.schemas.organization import InviteRequest, OrgCreateRequest, OrgCreateResponse
from app.schemas.user import UserOut


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.org_repo = OrgRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_org(self, user: User, data: OrgCreateRequest) -> OrgCreateResponse:
        org = await self.org_repo.create(name=data.org_name, created_by=user.id)
        await self.org_repo.add_member(user_id=user.id, org_id=org.id, role="admin")
        await self.audit_repo.create(
            org_id=org.id,
            user_id=user.id,
            action="create_org",
            metadata={"org_name": data.org_name},
        )
        return OrgCreateResponse(org_id=org.id)

    async def invite_user(self, admin: User, org_id: UUID, data: InviteRequest) -> dict:
        target_user = await self.user_repo.get_by_email(data.email)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        existing = await self.org_repo.get_membership(target_user.id, org_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization",
            )

        role = data.role if data.role in ("admin", "member") else "member"
        await self.org_repo.add_member(user_id=target_user.id, org_id=org_id, role=role)
        await self.audit_repo.create(
            org_id=org_id,
            user_id=admin.id,
            action="invite_user",
            metadata={"invited_email": data.email, "role": role},
        )
        return {"detail": "User invited successfully"}

    async def list_users(
        self, org_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[UserOut]:
        users = await self.org_repo.list_members(org_id, limit, offset)
        return [UserOut.model_validate(u) for u in users]

    async def search_users(
        self, org_id: UUID, query: str, limit: int = 20, offset: int = 0
    ) -> list[UserOut]:
        users = await self.user_repo.search_users_in_org(org_id, query, limit, offset)
        return [UserOut.model_validate(u) for u in users]
