from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.item_repo import ItemRepository
from app.repositories.org_repo import OrgRepository
from app.schemas.item import ItemCreateRequest, ItemCreateResponse, ItemOut


class ItemService:
    def __init__(self, db: AsyncSession):
        self.item_repo = ItemRepository(db)
        self.org_repo = OrgRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_item(
        self, user: User, org_id: UUID, data: ItemCreateRequest
    ) -> ItemCreateResponse:
        item = await self.item_repo.create(
            org_id=org_id, created_by=user.id, details=data.item_details
        )
        await self.audit_repo.create(
            org_id=org_id,
            user_id=user.id,
            action="create_item",
            metadata={"item_id": str(item.id)},
        )
        return ItemCreateResponse(item_id=item.id)

    async def list_items(
        self, user: User, org_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[ItemOut]:
        membership = await self.org_repo.get_membership(user.id, org_id)
        if membership and membership.role == "admin":
            items = await self.item_repo.list_all(org_id, limit, offset)
        else:
            items = await self.item_repo.list_by_creator(org_id, user.id, limit, offset)

        await self.audit_repo.create(
            org_id=org_id,
            user_id=user.id,
            action="view_items",
        )
        return [ItemOut.model_validate(i) for i in items]
