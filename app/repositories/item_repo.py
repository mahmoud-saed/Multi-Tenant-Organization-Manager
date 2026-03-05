from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item


class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, org_id: UUID, created_by: UUID, details: dict) -> Item:
        item = Item(org_id=org_id, created_by=created_by, details=details)
        self.db.add(item)
        await self.db.flush()
        return item

    async def list_all(self, org_id: UUID, limit: int = 20, offset: int = 0) -> list[Item]:
        stmt = (
            select(Item)
            .where(Item.org_id == org_id)
            .order_by(Item.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_creator(
        self, org_id: UUID, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[Item]:
        stmt = (
            select(Item)
            .where(Item.org_id == org_id, Item.created_by == user_id)
            .order_by(Item.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
