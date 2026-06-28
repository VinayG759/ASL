from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_API_KEYS = frozenset(
    {
        "asl_dev_change_me",
        "asl_dev_change_me_in_production",
        "test_api_key_for_ci",
    }
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    asl_env: str = "development"
    asl_log_level: str = "INFO"
    asl_api_key: str = "asl_dev_change_me"

    database_url: str = "postgresql+asyncpg://asl:asl_dev_password@localhost:5432/asl"
    database_url_sync: str = "postgresql+psycopg://asl:asl_dev_password@localhost:5432/asl"

    schema_version: str = "1.0"

    @field_validator("asl_api_key")
    @classmethod
    def api_key_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("ASL_API_KEY must not be empty")
        return value

    @model_validator(mode="after")
    def reject_insecure_defaults_outside_development(self) -> "Settings":
        if self.asl_env.lower() in {"development", "test"}:
            return self
        if self.asl_api_key in _INSECURE_API_KEYS:
            raise ValueError(
                "ASL_API_KEY is a known development default; "
                "set a strong key when ASL_ENV is not development"
            )
        if "asl_dev_password" in self.database_url or "asl_dev_password" in self.database_url_sync:
            raise ValueError(
                "DATABASE_URL uses development credentials; "
                "override for non-development deployments"
            )
        return self


settings = Settings()
