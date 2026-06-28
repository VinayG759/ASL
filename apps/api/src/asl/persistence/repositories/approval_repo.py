from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from asl.persistence.models.approval import ApprovalRequest


class ApprovalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_pending(self, limit: int = 20, offset: int = 0) -> list[ApprovalRequest]:
        result = await self._session.execute(
            select(ApprovalRequest)
            .where(ApprovalRequest.status == "PENDING")
            .order_by(ApprovalRequest.created_at)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_approval_id(self, approval_id: str) -> ApprovalRequest | None:
        result = await self._session.execute(
            select(ApprovalRequest).where(ApprovalRequest.approval_id == approval_id)
        )
        return result.scalar_one_or_none()
