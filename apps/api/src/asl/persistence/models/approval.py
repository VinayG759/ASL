from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from asl.persistence.database import Base

if TYPE_CHECKING:
    from asl.persistence.models.decision import DecisionRecord


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    approval_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decision_records.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    risk_tier: Mapped[str] = mapped_column(String(16), nullable=False)
    assigned_role: Mapped[str | None] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    decision_record: Mapped[DecisionRecord] = relationship(back_populates="approval_request")
    resolution: Mapped[ApprovalResolution | None] = relationship(
        back_populates="approval_request", uselist=False
    )


class ApprovalResolution(Base):
    __tablename__ = "approval_resolutions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    approval_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_requests.id"), unique=True, nullable=False
    )
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    approver_id: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    approval_request: Mapped[ApprovalRequest] = relationship(back_populates="resolution")
