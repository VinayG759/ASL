from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from asl.persistence.models.decision import DecisionRecord


class DecisionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_decision_id(self, decision_id: str) -> DecisionRecord | None:
        result = await self._session.execute(
            select(DecisionRecord).where(DecisionRecord.decision_id == decision_id)
        )
        return result.scalar_one_or_none()

    async def add(self, record: DecisionRecord) -> DecisionRecord:
        self._session.add(record)
        await self._session.flush()
        return record

    async def set_final_outcome(
        self, decision_id: str, final_outcome: str
    ) -> DecisionRecord | None:
        record = await self.get_by_decision_id(decision_id)
        if record is None:
            return None
        record.final_outcome = final_outcome
        await self._session.flush()
        return record
