from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from asl.persistence.models.policy import PolicyVersion


class PolicyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self) -> PolicyVersion | None:
        result = await self._session.execute(
            select(PolicyVersion).where(PolicyVersion.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def add(self, version: PolicyVersion) -> PolicyVersion:
        self._session.add(version)
        await self._session.flush()
        return version
