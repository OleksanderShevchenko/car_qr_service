from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.cars import crud as cars_crud
from src.car_qr_service.cars.schemas import PublicCarInfo
from src.car_qr_service.database.database import get_db_session

router = APIRouter(prefix="/public", tags=["public"])

# Вказуємо, де шукати шаблони
templates = Jinja2Templates(directory="src/car_qr_service/templates")


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


@router.post("/search", response_class=HTMLResponse)
async def search_car_for_htmx(
    request: Request,
    license_plate: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Цей ендпоінт є адаптером для HTMX. Він викликає існуючий API
    і перетворює його відповідь (JSON або помилку) на HTML.
    """
    context = {"request": request}
    try:
        # Викликаємо нашу існуючу, протестовану функцію
        car = await find_car_by_plate(license_plate, db)
        context["car"] = car
    except HTTPException as e:
        # Якщо API кинув помилку, ми її ловимо
        context["car"] = None
        context["detail"] = e.detail

    # Рендеримо відповідний HTML
    return templates.TemplateResponse("partials/car_result.html", context)