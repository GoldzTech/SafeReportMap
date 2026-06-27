from functools import lru_cache
from typing import List, Literal

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "SafeReport Map"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # App behavior
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Tenant foundation
    DEFAULT_TENANT_SLUG: str = "default"
    DEFAULT_TENANT_NAME: str = "Default Institution"
    TENANT_HEADER_NAME: str = "X-Tenant-Slug"
    TENANT_MODE: Literal["single", "header", "subdomain"] = "single"

    # Files / uploads
    MAX_UPLOAD_SIZE_MB: int = 10
    ATTACHMENTS_ENABLED: bool = True

    # AI / triage
    TRIAGE_ENABLED: bool = True
    TRIAGE_TIMEOUT_SECONDS: int = 5
    TRIAGE_MODEL_VERSION: str = "v1"
    TRIAGE_PIPELINE_VERSION: str = "v1"

    # Privacy / compliance
    STORE_RAW_CONTENT: bool = True
    STORE_SANITIZED_CONTENT: bool = True
    AUDIT_LOGGING_ENABLED: bool = True

    # Demo / seed
    DEMO_MODE: bool = False
    DEMO_ADMIN_EMAIL: str = "admin@safereport.com"
    DEMO_ADMIN_PASSWORD: str = ""

    # OpenAI
    AI_PROVIDER: Literal["hybrid", "openai", "rule_based"] = "hybrid"
    OPENAI_API_KEY: SecretStr | None = None
    OPENAI_MODEL: str = "gpt-5-nano"
    OPENAI_TIMEOUT_SECONDS: int = 45

    @property
    def cors_origins(self) -> List[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    @property
    def openai_api_key(self) -> str | None:
        return self.OPENAI_API_KEY.get_secret_value() if self.OPENAI_API_KEY else None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
