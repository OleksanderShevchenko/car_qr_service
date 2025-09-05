from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Визначаємо шлях до кореневої папки проєкту.
# Path(__file__) -> поточний файл (config.py)
# .parent -> папка (car_qr_service)
# .parent -> папка (src)
# .parent -> корінь проєкту
ROOT_DIR = Path(__file__).parent.parent.parent

# Визначаємо шлях до файлу бази даних у корені проєкту
DB_FILE = ROOT_DIR / "car_qr.db"
DB_URL = f"sqlite+aiosqlite:///{DB_FILE}"

class Settings(BaseSettings):
    """
    Клас для зберігання налаштувань додатку.
    Використовує pydantic-settings для завантаження налаштувань
    з .env файлу та змінних оточення.
    """
    # URL для підключення до бази даних
    DB_URL: str = DB_URL

    model_config = SettingsConfigDict(env_file=".env")


# Створюємо екземпляр налаштувань, який будемо використовувати у всьому додатку
settings = Settings()
