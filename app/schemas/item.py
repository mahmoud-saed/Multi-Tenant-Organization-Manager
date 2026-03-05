from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ItemCreateRequest(BaseModel):
    item_details: dict[str, Any]


class ItemCreateResponse(BaseModel):
    item_id: UUID


class ItemOut(BaseModel):
    id: UUID
    org_id: UUID
    created_by: UUID
    details: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
