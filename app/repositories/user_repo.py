from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, email: str, password_hash: str, full_name: str) -> User:
        user = User(email=email, password_hash=password_hash, full_name=full_name)
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def search_users_in_org(
        self, org_id: UUID, query: str, limit: int = 20, offset: int = 0
    ) -> list[User]:
        from app.models.membership import Membership

        ts_query = func.plainto_tsquery("english", query)
        ts_vector = func.to_tsvector(
            "english", User.email + text("' '") + User.full_name
        )

        stmt = (
            select(User)
            .join(Membership, Membership.user_id == User.id)
            .where(Membership.org_id == org_id)
            .where(ts_vector.op("@@")(ts_query))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
