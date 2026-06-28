import os

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://asl:asl_dev_password@localhost:5432/asl"
)

EXPECTED_TABLES = {
    "policy_versions",
    "decision_records",
    "approval_requests",
    "approval_resolutions",
    "session_context",
    "api_keys",
    "system_config",
}


@pytest.mark.asyncio
async def test_schema_tables_exist() -> None:
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        def _tables(sync_conn):  # noqa: ANN001
            return set(inspect(sync_conn).get_table_names())

        tables = await conn.run_sync(_tables)
    await engine.dispose()
    assert EXPECTED_TABLES.issubset(tables)


@pytest.mark.asyncio
async def test_decision_records_has_received_at_and_final_outcome() -> None:
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'decision_records'
                  AND column_name IN ('received_at', 'final_outcome')
                """
            )
        )
        columns = {row[0] for row in result}
    await engine.dispose()
    assert columns == {"received_at", "final_outcome"}
