from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User


class OrgRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, created_by: UUID) -> Organization:
        org = Organization(name=name, created_by=created_by)
        self.db.add(org)
        await self.db.flush()
        return org

    async def get_by_id(self, org_id: UUID) -> Organization | None:
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def add_member(self, user_id: UUID, org_id: UUID, role: str = "member") -> Membership:
        membership = Membership(user_id=user_id, org_id=org_id, role=role)
        self.db.add(membership)
        await self.db.flush()
        return membership

    async def get_membership(self, user_id: UUID, org_id: UUID) -> Membership | None:
        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.org_id == org_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_members(
        self, org_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[User]:
        stmt = (
            select(User)
            .join(Membership, Membership.user_id == User.id)
            .where(Membership.org_id == org_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
