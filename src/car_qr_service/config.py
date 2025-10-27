from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Function to find the project root
def find_project_root(marker_file=".env") -> Path:
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / marker_file).exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(
        f"Could not find project root containing {marker_file}"
    )


# Define the project root directory
PROJECT_ROOT = find_project_root()


class Settings(BaseSettings):
    """
    Main application settings class.
    Reads configuration values from environment variables and .env file.
    """

    # --- Database Settings ---
    # Read PostgreSQL connection details from environment variables
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "car_qr_service_db"
    # Construct the PostgreSQL database URL
    # Use f-string for clear formatting
    DB_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Define the SQLite URL for tests (using a file for reliability)
    TEST_DB_URL: str = f"sqlite+aiosqlite:///{PROJECT_ROOT}/test.db"

    # --- JWT Settings ---
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"

    # --- Pydantic Settings Configuration ---
    # Load settings from the .env file located in the project root
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", extra="ignore"
    )


# Create a single instance of the settings to be imported elsewhere
settings = Settings()
