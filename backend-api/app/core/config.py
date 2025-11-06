from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_path: str = "data/storms.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

