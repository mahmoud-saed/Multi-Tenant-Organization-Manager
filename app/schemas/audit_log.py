from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogOut(BaseModel):
    id: UUID
    org_id: UUID
    user_id: UUID
    action: str
    metadata: dict[str, Any] = Field(alias="metadata_")
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ChatbotRequest(BaseModel):
    question: str
    stream: bool = False


class ChatbotResponse(BaseModel):
    answer: str
