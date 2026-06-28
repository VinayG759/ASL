from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from asl.domain.models.reason_codes import GovernReasonCode


class Principal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["user", "service", "anonymous"]
    id: str = Field(min_length=1)


class DelegationHop(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1)
    role: str | None = None


class GovernRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    tool: str = Field(min_length=1, max_length=256)
    arguments: dict[str, Any]
    agent_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    timestamp: datetime
    principal: Principal
    delegation_chain: list[DelegationHop] = Field(default_factory=list, max_length=32)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernResponse(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    decision: Literal["ALLOW", "DENY", "ESCALATE"]
    decision_id: str = Field(pattern=r"^dec_")
    policy_version: str = Field(pattern=r"^v[0-9]+$")
    risk_tier: Literal["READ", "WRITE", "DESTRUCTIVE", "CRITICAL"]
    reason: str
    reason_code: GovernReasonCode
    approval_id: str | None = Field(default=None, pattern=r"^apr_")
    poll_url: str | None = None
    expires_at: datetime | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    schema_version: Literal["1.0"] = "1.0"


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] = Field(default_factory=list)
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
