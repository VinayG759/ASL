import os

import pytest
from httpx import AsyncClient

API_KEY = os.environ["ASL_API_KEY"]

GOVERN_BODY = {
    "schema_version": "1.0",
    "tool": "update_ticket",
    "arguments": {"ticket_id": "T-123"},
    "agent_id": "nexusflow/support-agent",
    "session_id": "sess_test",
    "timestamp": "2026-06-28T10:00:00Z",
    "principal": {"type": "user", "id": "user:U42"},
}


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["schema_version"] == "1.0"


@pytest.mark.asyncio
async def test_govern_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/api/v1/govern/tool-use", json=GOVERN_BODY)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_govern_rejects_wrong_api_key(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/govern/tool-use",
        json=GOVERN_BODY,
        headers={"Authorization": "Bearer wrong_key"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid or missing API key"


@pytest.mark.asyncio
async def test_govern_rejects_non_bearer_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/govern/tool-use",
        json=GOVERN_BODY,
        headers={"Authorization": f"Basic {API_KEY}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_govern_validation_error_returns_contract_shape(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/govern/tool-use",
        json={"schema_version": "1.0", "tool": "x"},
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in body["error"]
    assert response.headers.get("X-Request-ID")


@pytest.mark.asyncio
async def test_govern_rejects_unknown_fields(client: AsyncClient) -> None:
    body = {**GOVERN_BODY, "unexpected": True}
    response = await client.post(
        "/api/v1/govern/tool-use",
        json=body,
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_govern_stub_with_valid_key(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/govern/tool-use",
        json=GOVERN_BODY,
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOW"
    assert data["decision_id"].startswith("dec_")
    assert data["schema_version"] == "1.0"
    assert data["policy_version"] == "v0"
    assert data["reason_code"] == "STUB_RESPONSE"


@pytest.mark.asyncio
async def test_decision_status_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/govern/decisions/dec_abc/status")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_decision_status_not_found(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/govern/decisions/dec_abc/status",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_approvals_list_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/approvals")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_approvals_list_empty_with_auth(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/approvals",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {"schema_version": "1.0", "items": [], "total": 0}
