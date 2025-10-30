# src/car_qr_service/config.py
from pydantic_settings import BaseSettings

# БІЛЬШЕ НІЯКИХ find_project_root() АБО load_dotenv()!

class Settings(BaseSettings):
    # Pydantic АВТОМАТИЧНО зчитає це з середовища Render
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # Цей рядок НЕОБОВ'ЯЗКОВИЙ, але він корисний 
        # для локальної розробки, якщо .env все ж є
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

settings = Settings()