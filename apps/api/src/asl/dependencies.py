import secrets
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from asl.config import Settings, settings
from asl.domain.exceptions import ForbiddenError, UnauthorizedError
from asl.domain.models.auth import ApiKeyContext

_bearer = HTTPBearer(auto_error=False)
_AUTH_FAILURE_MESSAGE = "Invalid or missing API key"


def get_settings() -> Settings:
    return settings


async def get_api_key_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer)],
    cfg: Annotated[Settings, Depends(get_settings)],
) -> ApiKeyContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError(_AUTH_FAILURE_MESSAGE)

    if not secrets.compare_digest(credentials.credentials, cfg.asl_api_key):
        raise UnauthorizedError(_AUTH_FAILURE_MESSAGE)

    return ApiKeyContext(
        key_id="env:v0",
        scopes=["govern:write", "govern:read", "admin:read", "admin:write"],
    )


def require_scope(
    scope: str,
) -> Callable[..., Awaitable[ApiKeyContext]]:
    async def _check(
        ctx: Annotated[ApiKeyContext, Depends(get_api_key_context)],
    ) -> ApiKeyContext:
        if not ctx.has_scope(scope):
            raise ForbiddenError(f"API key lacks required scope: {scope}")
        return ctx

    return _check


SettingsDep = Annotated[Settings, Depends(get_settings)]
ApiKeyDep = Annotated[ApiKeyContext, Depends(get_api_key_context)]
GovernWriteDep = Annotated[ApiKeyContext, Depends(require_scope("govern:write"))]
GovernReadDep = Annotated[ApiKeyContext, Depends(require_scope("govern:read"))]
AdminReadDep = Annotated[ApiKeyContext, Depends(require_scope("admin:read"))]
AdminWriteDep = Annotated[ApiKeyContext, Depends(require_scope("admin:write"))]
