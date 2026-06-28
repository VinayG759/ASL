import os

# Set test env before importing the application (settings load at import time).
os.environ.setdefault("ASL_ENV", "test")
os.environ.setdefault("ASL_API_KEY", "test_api_key_for_ci")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://asl:asl_dev_password@localhost:5432/asl",
)
os.environ.setdefault(
    "DATABASE_URL_SYNC",
    "postgresql+psycopg://asl:asl_dev_password@localhost:5432/asl",
)

import pytest
from httpx import ASGITransport, AsyncClient

from asl.main import app

API_KEY = os.environ["ASL_API_KEY"]


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


GOVERN_BODY = {
    "schema_version": "1.0",
    "tool": "update_ticket",
    "arguments": {"ticket_id": "T-123"},
    "agent_id": "nexusflow/support-agent",
    "session_id": "sess_test",
    "timestamp": "2026-06-28T10:00:00Z",
    "principal": {"type": "user", "id": "user:U42"},
}
