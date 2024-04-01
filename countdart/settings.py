""" Define all setttings which are used by the backend. It will attempt
to determine the values of any fields by reading from the environment.
Default values will be used if no matching environment variable is set
"""
from pydantic import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings which are read from the environment

    Args:
        BaseSettings (_type_): _description_
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", case_sensitive=True, extra="ignore"
    )

    API_V1_STR: str = "/api/v1"

    # Mongodb settings
    MONGO_DB_DATABASE: str = "dashboard"
    MONGO_DB_SERVER: MongoDsn = "mongodb://localhost:27017"

    # Celery settings
    CELERY_BROKER: str = "redis://redis:6379/0"
    CELERY_BACKEND: str = "redis://redis:6379/1"


settings = Settings()
