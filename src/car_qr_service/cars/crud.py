from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.car_qr_service.cars.schemas import CarCreate, CarUpdate
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

async def get_car_by_id(db: AsyncSession, car_id: int) -> Car | None:
    """Отримує автомобіль за його ID."""
    result = await db.execute(select(Car).filter(Car.id == car_id))
    return result.scalars().first()


async def update_car(db: AsyncSession, car: Car, car_update: CarUpdate) -> Car:
    """Оновлює дані автомобіля."""
    update_data = car_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(car, key, value)
    await db.commit()
    await db.refresh(car)
    return car


async def delete_car(db: AsyncSession, car: Car):
    """Видаляє автомобіль з бази даних."""
    await db.delete(car)
    await db.commit()


async def get_car_by_license_plate(db: AsyncSession, license_plate: str) -> Car | None:
    """
    Отримує автомобіль за його номерним знаком.
    В оптимізованому варіанті додаємо дані про користувача,
    Щоб в шаблоні результатів відображати телефон, якщо користувач дозволив
    """
    query = (
        select(Car)
        .options(selectinload(Car.owner))  # add user data
        .where(Car.license_plate == license_plate)
    )
    result = await db.execute(query)
    return result.scalars().first()
