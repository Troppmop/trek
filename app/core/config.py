import os
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str | None = None

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "trek_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    @computed_field
    @property
    def ASYNC_POSTGRES_URL(self) -> str:
        db_url = str(self.DATABASE_URL or "").strip()
        
        if db_url and "://" in db_url:
            # 1. Standardize the prefix first
            if db_url.startswith("postgres://"):
                url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
                url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                url = db_url

            # 2. Fix the "Empty Password" or "Empty Port" issues WITHOUT breaking the protocol
            # We only replace ':/' if it's NOT the one in 'asyncpg://'
            # A safer way is to just fix the specific Railway ':@' glitch
            url = url.replace(":@", "@")
            
            # If there's a trailing colon before the slash in the path (e.g., host:/db)
            if ":/" in url and ":// " not in url.replace("://", "IGNORE", 1):
                # This logic ensures we don't trip over the main protocol colon
                parts = url.split("://", 1)
                parts[1] = parts[1].replace(":/", "/")
                url = "://".join(parts)
                
            return url

        # 2. Manual Fallback
        auth = f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@" if self.POSTGRES_PASSWORD else f"{self.POSTGRES_USER}@"
        return f"postgresql+asyncpg://{auth}{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()