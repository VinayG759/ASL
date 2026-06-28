from typing import Literal

from fastapi import APIRouter, Path, Query

from asl.dependencies import AdminReadDep, AdminWriteDep
from asl.domain.exceptions import NotFoundError
from asl.domain.models.approval import (
    ApprovalActionRequest,
    ApprovalListResponse,
)

router = APIRouter(prefix="/approvals")


@router.get("", response_model=ApprovalListResponse)
async def list_approvals(
    _auth: AdminReadDep,
    status: Literal["PENDING", "APPROVED", "REJECTED", "EXPIRED"] = Query(default="PENDING"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ApprovalListResponse:
    """Phase 0 stub — returns empty queue; implementation in Phase 1."""
    _ = status, limit, offset
    return ApprovalListResponse(items=[], total=0)


@router.post("/{approval_id}/approve")
async def approve_request(
    _auth: AdminWriteDep,
    approval_id: str = Path(pattern=r"^apr_"),
    _body: ApprovalActionRequest | None = None,
) -> None:
    raise NotFoundError(f"Approval {approval_id} not found")


@router.post("/{approval_id}/reject")
async def reject_request(
    _auth: AdminWriteDep,
    approval_id: str = Path(pattern=r"^apr_"),
    _body: ApprovalActionRequest | None = None,
) -> None:
    raise NotFoundError(f"Approval {approval_id} not found")
