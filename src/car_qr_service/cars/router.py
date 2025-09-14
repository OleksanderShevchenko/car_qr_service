from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import get_current_user
from src.car_qr_service.cars import crud
from src.car_qr_service.cars.schemas import CarCreate, CarRead, CarUpdate
from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.database.models import User

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post(
    "/",
    response_model=CarRead,
    status_code=status.HTTP_201_CREATED,
    summary="Додати новий автомобіль",
)
async def add_new_car(
    body: CarCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Endpoint для додавання нового автомобіля для залогіненого користувача.
    - **body**: Дані нового автомобіля.
    - **current_user**: Поточний користувач (отримується з токену).
    - **db**: Сесія бази даних.
    """
    new_car = await crud.create_car(db=db, car=body, owner_id=current_user.id)
    return new_car


@router.get(
    "/",
    response_model=list[CarRead],
    summary="Отримати список своїх автомобілів"
)
async def get_my_cars(
    # Ця залежність робить ендпоінт захищеним.
    # Якщо токен невалідний, код далі не виконається.
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Endpoint для отримання списку автомобілів,
    що належать поточному залогіненому користувачу.
    """
    # Ми передаємо ID поточного користувача в CRUD-функцію,
    # щоб отримати тільки його автомобілі.
    cars = await crud.get_user_cars(db=db, owner_id=current_user.id)
    return cars


@router.patch(
    "/{car_id}", response_model=CarRead, summary="Оновити дані автомобіля"
)
async def update_car_details(
    car_id: int,
    body: CarUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Endpoint для оновлення даних автомобіля. Оновити авто може тільки його власник."""
    db_car = await crud.get_car_by_id(db, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")
    if db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостатньо прав для оновлення цього автомобіля"
        )
    updated_car = await crud.update_car(db=db, car=db_car, car_update=body)
    return updated_car


@router.delete(
    "/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити автомобіль",
)
async def delete_car_by_id(
    car_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Endpoint для видалення автомобіля.
    Видалити авто може тільки його власник.
    """
    # 1. Отримуємо авто з бази даних
    db_car = await crud.get_car_by_id(db, car_id=car_id)

    # 2. Перевіряємо, чи авто існує і чи належить воно поточному користувачу
    if db_car is None:
        # Щоб уникнути можливості з'ясувати існування чужих авто,
        # можна завжди повертати 204, навіть якщо авто не знайдено.
        # Але для чіткості API повернемо 404.
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")
    if db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостатньо прав для видалення цього автомобіля"
        )

    # 3. Видаляємо авто
    await crud.delete_car(db=db, car=db_car)

    # При успішному видаленні з кодом 204 відповідь не повинна мати тіла.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

