"""
Configuration settings for the IBTrACS database updater
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Settings for database updater"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    # Database connection settings
    # If USE_LOCAL_DB is True, these are ignored and local Docker Compose DB is used
    USE_LOCAL_DB: bool = False
    
    # Remote database connection (used when USE_LOCAL_DB=False)
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    # IBTrACS data source
    IBTRACS_CSV_URL: str = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.ALL.list.v04r01.csv"
    
    @property
    def database_url(self) -> str:
        """
        Get the database connection URL.
        If USE_LOCAL_DB is True, returns local Docker Compose connection string.
        Otherwise, constructs connection string from DB_* environment variables.
        """
        if self.USE_LOCAL_DB:
            # Local Docker Compose database
            return "postgresql://ibtracs:ibtracs_dev@localhost:5432/ibtracs"
        else:
            # Remote database
            if not all([self.DB_HOST, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
                raise ValueError(
                    "When USE_LOCAL_DB=False, DB_HOST, DB_NAME, DB_USER, and DB_PASSWORD must be set"
                )
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

