from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "OnboardX"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/onboardx"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
