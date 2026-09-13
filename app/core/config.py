"""Application settings loaded from environment variables and an optional .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = (
        "postgresql+asyncpg://ppp_user:change-me@localhost:5432/pppp_db"
    )
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "PPPProfile"
    VERSION: str = "2.0.0"


settings = Settings()
