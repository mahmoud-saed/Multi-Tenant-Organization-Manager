from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_member
from app.db.session import get_db
from app.models.user import User
from app.schemas.item import ItemCreateRequest, ItemCreateResponse, ItemOut
from app.services.item_service import ItemService

router = APIRouter()


@router.post("/organizations/{org_id}/items", response_model=ItemCreateResponse, status_code=201)
async def create_item(
    org_id: UUID,
    data: ItemCreateRequest,
    user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    return await ItemService(db).create_item(user, org_id, data)


@router.get("/organizations/{org_id}/items", response_model=list[ItemOut])
async def list_items(
    org_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db),
):
    return await ItemService(db).list_items(user, org_id, limit, offset)
