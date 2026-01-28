from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "Hide and Seek"
    debug: bool = False
    secret_key: str = ""

    # Database
    database_url: str = ""

    # Redis
    redis_url: str = ""

    # JWT
    jwt_algorithm: str = ""
    jwt_expiration_hours: int = 24 * 7  # 1 week

    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = ""

    # Frontend
    frontend_url: str = ""

    # Team settings
    team_lock_days: int = 60
    max_team_size: int = 4
    min_team_size: int = 1
    join_request_expiry_hours: int = 24

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
