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
# Specify where to look for templates
templates = Jinja2Templates(directory="src/car_qr_service/templates")


@router.get(
    "/cars/{license_plate}",
    response_model=PublicCarInfo,
    summary="Знаходимо автомобіль за державним номером реєстрації " +
            "(Find auto by its license plate and get public infor)",
)
async def find_car_by_plate(
    license_plate: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Публічний endpoint для пошуку автомобіля за його номерним знаком.
    Повертає тільки безпечну інформацію (марка, модель).

    Public endpoint for searching for a car by its license plate.
    Returns only secure information (make, model).
    """
    db_car = await cars_crud.get_car_by_license_plate(db, license_plate=license_plate)
    if db_car is None:
        raise HTTPException(status_code=404, detail=f"Автомобіль з таким номером не знайдено." +
                                                    f" (Car with {license_plate} number is not found)")
    return db_car


@router.post("/search",
             response_class=HTMLResponse,
             summary="Знаходимо автомобіль за державним номером реєстрації " +
                     "(Find auto by its license plate and get public infor)")
async def search_car_for_htmx(
    request: Request,
    license_plate: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Цей ендпоінт є адаптером для HTMX. Він викликає існуючий API,
    і перетворює його відповідь (JSON або помилку) на HTML.
    This endpoint is an adapter for HTMX. It calls an existing API,
    and converts its response (JSON or error) to HTML.
    """
    context = {"request": request}
    try:
        # Викликаємо нашу існуючу, протестовану функцію
        # Call our existing, tested function
        car = await find_car_by_plate(license_plate, db)
        context["car"] = car
    except HTTPException as e:
        # Якщо API кинув помилку, ми її ловимо
        # If the API throws an error, we catch it
        context["car"] = None
        context["detail"] = e.detail

    # Рендеримо відповідний HTML
    # Render the corresponding HTML
    return templates.TemplateResponse(request, "partials/car_result.html", context)


@router.post("/send-sms/{license_plate}", response_class=HTMLResponse)
async def send_sms_stub(
    license_plate: str,
    message: Annotated[str, Form()],
):
    """
    Ендпоінт-заглушка для форми відправки SMS.
    Наразі він не робить нічого, лише повертає повідомлення про успіх.
    Endpoint stub for SMS sending form.
    Currently it does nothing but returns a success message.
    """
    # У майбутньому тут буде логіка інтеграції з SMS-сервісом.
    # Ми б використовували `license_plate`, щоб знайти номер власника.
    # In the future, there will be logic here to integrate with the SMS service.
    # We would use `license_plate` to find the owner's number.
    print(f"Імітація відправки SMS для авто {license_plate} з повідомленням: '{message}'")

    # Повертаємо простий HTML, який HTMX вставить у div#sms-status
    return HTMLResponse(
        content='<span class="text-green-600">✓ Повідомлення надіслано!</span>'
    )


# --- НОВИЙ ЕНДПОІНТ №4: ЗАГЛУШКА ДЛЯ ДЗВІНКА ---
@router.post("/initiate-call", response_class=HTMLResponse)
async def initiate_call_stub(
    request: Request,
    license_plate: Annotated[str, Form()],
):
    """
    Ендпоінт-заглушка для імітації телефонного дзвінка.
    """
    print(f"Initiating call to owner of {license_plate}")
    return templates.TemplateResponse(
        request, "partials/call_success.html", {"license_plate": license_plate}
    )