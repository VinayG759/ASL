import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from asl.domain.exceptions import ASLError
from asl.domain.models.govern import ErrorDetail, ErrorResponse

_MAX_REQUEST_ID_LEN = 128


def _sanitize_request_id(raw: str | None) -> str | None:
    if raw is None:
        return None
    cleaned = raw.strip()
    if not cleaned or len(cleaned) > _MAX_REQUEST_ID_LEN:
        return None
    return cleaned


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = _sanitize_request_id(request.headers.get("X-Request-ID")) or (
            f"req_{uuid.uuid4().hex[:12]}"
        )
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        except ASLError as exc:
            body = ErrorResponse(
                error=ErrorDetail(
                    code=exc.code,
                    message=exc.message,
                    request_id=request_id,
                )
            )
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=exc.status_code,
                content=body.model_dump(),
                headers={"X-Request-ID": request_id},
            )
