import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from asl.domain.models.govern import ErrorDetail, ErrorResponse


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID") or (
        f"req_{uuid.uuid4().hex[:12]}"
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _request_id(request)
    details = [dict(error) for error in exc.errors()]
    body = ErrorResponse(
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request body failed validation",
            details=details,
            request_id=request_id,
        )
    )
    return JSONResponse(
        status_code=400,
        content=body.model_dump(),
        headers={"X-Request-ID": request_id},
    )
