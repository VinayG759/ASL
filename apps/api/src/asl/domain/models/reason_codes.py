from typing import Literal

GovernReasonCode = Literal[
    "POLICY_ALLOW",
    "POLICY_DENY",
    "POLICY_ESCALATE",
    "UNCLASSIFIED_ESCALATE",
    "UNCLASSIFIED_DENY",
    "STUB_RESPONSE",
]

ApprovalReasonCode = Literal[
    "APPROVAL_APPROVED",
    "APPROVAL_REJECTED",
    "APPROVAL_EXPIRED",
]

ReasonCode = GovernReasonCode | ApprovalReasonCode
