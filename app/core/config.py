from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    app_name: str = "Locust Data Service"
    debug: bool = False
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    database_type: Literal["postgres", "snowflake"] = "postgres"

    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "locust_data"

    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_database: str = ""
    snowflake_schema: str = "public"
    snowflake_warehouse: str = ""

    @property
    def database_url(self) -> str:
        """Get database connection URL based on database type."""
        if self.database_type == "postgres":
            return (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        elif self.database_type == "snowflake":
            return (
                f"snowflake://{self.snowflake_user}:{self.snowflake_password}"
                f"@{self.snowflake_account}/{self.snowflake_database}/{self.snowflake_schema}"
                f"?warehouse={self.snowflake_warehouse}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        if self.database_type == "postgres":
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        elif self.database_type == "snowflake":
            return (
                f"snowflake://{self.snowflake_user}:{self.snowflake_password}"
                f"@{self.snowflake_account}/{self.snowflake_database}/{self.snowflake_schema}"
                f"?warehouse={self.snowflake_warehouse}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")


# Global settings instance
settings = Settings()
