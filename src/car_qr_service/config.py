from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Клас для зберігання налаштувань додатку.
    Використовує pydantic-settings для завантаження налаштувань
    з .env файлу та змінних оточення.
    """
    # URL для підключення до бази даних
    DB_URL: str = "sqlite+aiosqlite:///./car_qr.db"

    model_config = SettingsConfigDict(env_file=".env")


# Створюємо екземпляр налаштувань, який будемо використовувати у всьому додатку
settings = Settings()
