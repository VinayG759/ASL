from pydantic import BaseModel, Field


class ApiKeyContext(BaseModel):
    key_id: str
    scopes: list[str] = Field(default_factory=list)

    def has_scope(self, scope: str) -> bool:
        if scope in self.scopes:
            return True
        prefix = scope.split(":")[0]
        return f"{prefix}:*" in self.scopes or "admin:*" in self.scopes
