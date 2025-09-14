from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.cars.schemas import CarCreate
from src.car_qr_service.database.models import Car


async def create_car(db: AsyncSession, car: CarCreate, owner_id: int) -> Car:
    """
    Створює новий запис про автомобіль в базі даних.
    :param db: Сесія бази даних.
    :param car: Pydantic-схема з даними про автомобіль.
    :param owner_id: ID користувача, який є власником.
    :return: Об'єкт SQLAlchemy моделі Car.
    """
    db_car = Car(**car.model_dump(), owner_id=owner_id)
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car


async def get_user_cars(db: AsyncSession, owner_id: int) -> list[Car]:
    """
    Повертає список автомобілів, що належать конкретному користувачу.
    :param db: Сесія бази даних.
    :param owner_id: ID користувача-власника.
    :return: Список об'єктів SQLAlchemy моделі Car.
    """
    query = select(Car).where(Car.owner_id == owner_id)
    result = await db.execute(query)
    return list(result.scalars().all())
