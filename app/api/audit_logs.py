from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogOut, ChatbotRequest, ChatbotResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.get(
    "/organizations/{org_id}/audit-logs",
    response_model=list[AuditLogOut],
)
async def list_audit_logs(
    org_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AuditService(db).list_logs(org_id, limit, offset)


@router.post("/organizations/{org_id}/audit-logs/ask")
async def ask_chatbot(
    org_id: UUID,
    data: ChatbotRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AuditService(db)
    result = await service.ask_chatbot(org_id, data.question, data.stream)

    if data.stream:
        return StreamingResponse(result, media_type="text/event-stream")

    return ChatbotResponse(answer=result)
