from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from asl.persistence.models.api_key import ApiKey


class KeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_key_id(self, key_id: str) -> ApiKey | None:
        result = await self._session.execute(select(ApiKey).where(ApiKey.key_id == key_id))
        return result.scalar_one_or_none()

    async def list_active(self) -> list[ApiKey]:
        result = await self._session.execute(select(ApiKey).where(ApiKey.is_active.is_(True)))
        return list(result.scalars().all())
