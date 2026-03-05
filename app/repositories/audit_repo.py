from datetime import date, datetime, time, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, org_id: UUID, user_id: UUID, action: str, metadata: dict | None = None
    ) -> AuditLog:
        log = AuditLog(
            org_id=org_id,
            user_id=user_id,
            action=action,
            metadata_=metadata or {},
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def list_by_org(
        self, org_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.org_id == org_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_today_logs(self, org_id: UUID) -> list[AuditLog]:
        today_start = datetime.combine(date.today(), time.min, tzinfo=timezone.utc)
        stmt = (
            select(AuditLog)
            .where(AuditLog.org_id == org_id, AuditLog.created_at >= today_start)
            .order_by(AuditLog.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
