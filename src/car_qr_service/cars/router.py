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
    summary="Додати новий автомобіль для поточного користувача. (Add new car for logged in user)",
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

    Endpoint for adding a new car for a logged in user.
    - **body**: New car data.
    - **current_user**: Current user (obtained from token).
    - **db**: Database session.
    """
    new_car = await crud.create_car(db=db, car=body, owner_id=current_user.id)
    return new_car


@router.get(
    "/",
    response_model=list[CarRead],
    summary="Отримати список своїх автомобілів. (Get list of my cars)"
)
async def get_my_cars(
    # Ця залежність робить ендпоінт захищеним.
    # Якщо токен невалідний, код далі не виконається.
    # This dependency makes the endpoint secure.
    # If the token is invalid, the code will not continue.
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Endpoint для отримання списку автомобілів,
    що належать поточному залогіненому користувачу.
    Endpoint to get a list of cars owned by the currently logged in user.
    """
    # Ми передаємо ID поточного користувача в CRUD-функцію,
    # щоб отримати тільки його автомобілі.
    # We pass the current user's ID to the CRUD function,
    # to get only their cars.
    cars = await crud.get_user_cars(db=db, owner_id=current_user.id)
    return cars


@router.patch(
    "/{car_id}",
    response_model=CarRead,
    summary="Оновити дані вибраного автомобіля. (Update data of selected car)"
)
async def update_car_details(
    car_id: int,
    body: CarUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Endpoint для оновлення даних автомобіля.
    Оновити авто може тільки його власник.
    Endpoint for updating vehicle data.
    Only the owner of the vehicle can update the vehicle.
    """
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
    summary="Видалити вибраний автомобіль. (Delete selected car)",
)
async def delete_car_by_id(
    car_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Endpoint для видалення автомобіля.
    Видалити авто може тільки його власник.
    Endpoint for deleting a car.
    Only the owner can delete a car.
    """
    # 1. Отримуємо авто з бази даних
    #    Getting cars from the database
    db_car = await crud.get_car_by_id(db, car_id=car_id)

    # 2. Перевіряємо, чи авто існує і чи належить воно поточному користувачу
    #    Checking whether the car exists and whether it belongs to the current user
    if db_car is None:
        # Щоб уникнути можливості з'ясувати існування чужих авто,
        # можна завжди повертати 204, навіть якщо авто не знайдено.
        # Але для чіткості API повернемо 404.
        # To avoid the possibility of finding out the existence of other people's cars,
        # you can always return 204, even if the car is not found.
        # But for API clarity, we will return 404.
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")
    if db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостатньо прав для видалення цього автомобіля"
        )

    # 3. Видаляємо авто
    #    remove the car
    await crud.delete_car(db=db, car=db_car)

    # При успішному видаленні з кодом 204 відповідь не повинна мати тіла.
    #  If the deletion is successful with code 204, the response should not have a body.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

