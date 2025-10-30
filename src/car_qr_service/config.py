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

    # --- АВТОМАТИЧНО СТВОРЕНА ЗМІННА ---
    @computed_field
    @property
    def DB_URL(self) -> str:
        """
        Автоматично збирає URL для підключення до бази даних.
        Використовуємо 'postgresql+asyncpg', оскільки ми
        використовуємо create_async_engine.
        """
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    class Config:
        # Це допоможе вам локально, але не вплине на Render
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Створюємо єдиний екземпляр налаштувань для всього проєкту
settings = Settings()