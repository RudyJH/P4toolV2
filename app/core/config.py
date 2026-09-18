""" Application settings loaded from environment variables and an optional .env file.
    This module defines the Settings class, which uses Pydantic's BaseSettings to load
    configuration values for the application.
    The settings include database connection details, security parameters, and application metadata.
    The settings can be overridden by environment variables or a .env file, allowing for 
    flexible configuration in different environments (development, testing, production)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "sqlite+aiosqlite:///./ppp_dev.db"
    SECRET_KEY: str = "qweasd12"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "PPPProfile"
    DB_INIT: int = 1
    VERSION: str = "2.0.0"


settings = Settings()
