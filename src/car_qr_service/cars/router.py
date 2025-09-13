from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import get_current_user
from src.car_qr_service.cars import crud
from src.car_qr_service.cars.schemas import CarCreate, CarRead
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
