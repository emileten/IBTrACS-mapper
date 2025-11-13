from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_LOCAL_URL = "postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs"


class Settings(BaseSettings):
    """Application settings for database connectivity."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    CORS_ORIGINS: str | None = None

    # Optional fully-qualified connection string
    DATABASE_URL: Optional[str] = None

    # Optional components, used only if DATABASE_URL is not provided
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Return the PostgreSQL connection string to use."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if all([self.DB_HOST, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            return (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

        # Fall back to local defaults (Docker Compose / developer machine)
        return DEFAULT_LOCAL_URL

    @property
    def cors_origins(self) -> list[str] | None:
        if not self.CORS_ORIGINS:
            return None
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()

