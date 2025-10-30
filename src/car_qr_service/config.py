from pydantic import computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- 5 змінних, які ми додали в Render ---
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int

    # --- Ваші JWT змінні ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- 1. АСИНХРОННИЙ URL (для FastAPI) ---
    @computed_field
    @property
    def DB_URL(self) -> str:
        """Асинхронний URL для FastAPI"""
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}?ssl=require"
        )

    # --- 2. СИНХРОННИЙ URL (для Alembic) ---
    @computed_field
    @property
    def SYNC_DB_URL(self) -> str:
        """Синхронний URL для Alembic (використовує psycopg)"""
        return (
            f"postgresql+psycopg://"  # <--- Ключова зміна
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}?ssl=require"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()