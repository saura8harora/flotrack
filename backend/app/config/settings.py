import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = (
        SettingsConfigDict(
            env_file=str(ENV_FILE),
            env_file_encoding="utf-8",
            extra="ignore",
        )
        if ENV_FILE.exists()
        else SettingsConfigDict(extra="ignore")
    )

    MONGO_URI: str = ""
    DATABASE_NAME: str = "flotrack_db"
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

        vercel_url = os.getenv("VERCEL_URL")
        if vercel_url:
            origins.append(f"https://{vercel_url}")

        vercel_branch_url = os.getenv("VERCEL_BRANCH_URL")
        if vercel_branch_url:
            origins.append(f"https://{vercel_branch_url}")

        production_url = os.getenv("VERCEL_PROJECT_PRODUCTION_URL")
        if production_url:
            origins.append(f"https://{production_url}")

        return list(dict.fromkeys(origins))
    @property
    def has_database_config(self) -> bool:
        return bool(self.MONGO_URI.strip())

    @property
    def has_jwt_config(self) -> bool:
        return bool(self.JWT_SECRET.strip())


settings = Settings()
