class ASLError(Exception):
    """Base ASL domain error."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedError(ASLError):
    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenError(ASLError):
    def __init__(self, message: str = "Insufficient scope") -> None:
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class NotFoundError(ASLError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(code="NOT_FOUND", message=message, status_code=404)


class ConflictError(ASLError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(code="CONFLICT", message=message, status_code=409)
