"""
Configuration settings for the IBTrACS database updater
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_LOCAL_URL = "postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs"


class Settings(BaseSettings):
    """Settings for database updater."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Optional full connection string
    DATABASE_URL: Optional[str] = None

    # Optional connection components (used if DATABASE_URL is absent)
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    # IBTrACS data source
    IBTRACS_CSV_URL: str = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.ALL.list.v04r01.csv"

    @property
    def database_url(self) -> str:
        """Get the database connection URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if all([self.DB_HOST, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            return (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

        return DEFAULT_LOCAL_URL


settings = Settings()

