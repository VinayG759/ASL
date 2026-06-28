from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ApprovalListQuery(BaseModel):
    status: Literal["PENDING", "APPROVED", "REJECTED", "EXPIRED"] = "PENDING"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ApprovalSummary(BaseModel):
    approval_id: str
    decision_id: str
    status: str
    risk_tier: str
    expires_at: datetime | None = None
    created_at: datetime


class ApprovalListResponse(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    items: list[ApprovalSummary]
    total: int


class ApprovalActionRequest(BaseModel):
    approver_id: str | None = None
    reason: str | None = None


class DecisionStatusResponse(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    decision_id: str
    status: Literal["PENDING", "APPROVED", "REJECTED", "EXPIRED"]
    final_outcome: Literal["ALLOW", "DENY"] | None = None
    resolved_at: datetime | None = None
