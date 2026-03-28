"""Config file for the application. 

This file defines the Settings class which holds all the configuration values for the application. 
It uses Pydantic's BaseSettings to automatically read from environment variables. 

The get_settings function is decorated with lru_cache to ensure that the settings are only loaded
once and cached for future use.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Settings class that holds all the configuration values for the application.

    Args:
        BaseSettings: BaseSettings is a class that allows us to define settings 
        that can be read from environment variables.
    
    Returns:
        Settings: An instance of the Settings class with the configuration values.
    """

    # application properties
    app_name: str = "Hide and Seek"
    debug: bool = False
    secret_key: str = ""

    # database properties
    database_url: str = ""

    # jwt properties
    jwt_algorithm: str = ""
    jwt_expiration_hours: int = 24 * 7  # 1 week

    # google oauth properties
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = ""

    # frontend properties
    frontend_url: str = ""

    # team settings
    team_lock_days: int = 60
    max_team_size: int = 4
    min_team_size: int = 1
    join_request_expiry_hours: int = 24

    class Config:
        env_file = None


@lru_cache()
def get_settings() -> Settings:
    """Get the application settings.

    Returns:
        Settings: An instance of the Settings class with the configuration values.
    """
    return Settings()


settings = get_settings()
