from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class Settings(BaseSettings):
    APP_NAME: str = "OnboardX"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/onboardx"
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if value is None or value == "":
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                import json
                value = json.loads(value)
            else:
                value = value.split(",")
        if not isinstance(value, (list, tuple, set)):
            raise ValueError("ALLOWED_ORIGINS must be a comma-separated list or JSON array")
        return list(dict.fromkeys(origin.strip().rstrip("/") for origin in value if origin and origin.strip()))

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
