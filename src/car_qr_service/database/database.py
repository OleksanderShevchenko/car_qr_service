from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.car_qr_service.config import settings

# Створюємо асинхронний "двигун" для взаємодії з базою даних.
# echo=True дозволяє бачити згенеровані SQL-запити в консолі (корисно для дебагу).
engine = create_async_engine(settings.DB_URL, echo=True)

# Створюємо фабрику асинхронних сесій.
# Кожна сесія - це окремий "діалог" з базою даних.
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


# Створюємо базовий клас для наших моделей.
# Всі наші моделі (User, Car) будуть успадковуватись від нього.
class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncSession:
    """
    Функція-генератор для отримання сесії бази даних.
    Використовується в FastAPI Depends для керування сесіями.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()