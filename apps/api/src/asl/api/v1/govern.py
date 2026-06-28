import uuid
from typing import Annotated

from fastapi import APIRouter, Header, Path

from asl.dependencies import GovernReadDep, GovernWriteDep
from asl.domain.exceptions import NotFoundError
from asl.domain.models.approval import DecisionStatusResponse
from asl.domain.models.govern import GovernRequest, GovernResponse

router = APIRouter(prefix="/govern")


@router.post("/tool-use", response_model=GovernResponse)
async def govern_tool_use(
    body: GovernRequest,
    _auth: GovernWriteDep,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key", max_length=128)] = None,
) -> GovernResponse:
    """Phase 0 stub — authenticates and validates request; policy engine ships Phase 1."""
    _ = idempotency_key
    decision_id = f"dec_{uuid.uuid4().hex}"
    return GovernResponse(
        decision="ALLOW",
        decision_id=decision_id,
        policy_version="v0",
        risk_tier="READ",
        reason="Phase 0 stub — policy engine not yet implemented",
        reason_code="STUB_RESPONSE",
    )


@router.get("/decisions/{decision_id}/status", response_model=DecisionStatusResponse)
async def get_decision_status(
    _auth: GovernReadDep,
    decision_id: str = Path(pattern=r"^dec_"),
) -> DecisionStatusResponse:
    """Phase 0 stub — returns 404 until decision persistence ships in Phase 1."""
    raise NotFoundError(f"Decision {decision_id} not found")
