from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.cars import crud as cars_crud
from src.car_qr_service.cars.schemas import PublicCarInfo
from src.car_qr_service.database.database import get_db_session

router = APIRouter(prefix="/public", tags=["public"])


@router.get(
    "/cars/{license_plate}",
    response_model=PublicCarInfo,
    summary="Find auto by its license plate and get public infor",
)
async def find_car_by_plate(
    license_plate: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Публічний endpoint для пошуку автомобіля за його номерним знаком.
    Повертає тільки безпечну інформацію (марка, модель).
    """
    db_car = await cars_crud.get_car_by_license_plate(db, license_plate=license_plate)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Автомобіль з таким номером не знайдено")
    return db_car
