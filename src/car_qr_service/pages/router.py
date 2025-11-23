from typing import Annotated, Optional
import qrcode
import io

from fastapi import APIRouter, Request, Depends, Form, Request, Response, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import get_current_user, authenticate_user, create_access_token, \
    get_current_user_from_cookie
from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.database.models import User
from src.car_qr_service.users import crud as users_crud
from src.car_qr_service.cars import crud as cars_crud
from src.car_qr_service.users.schemas import UserCreate
from src.car_qr_service.cars.schemas import CarCreate

# Створюємо роутер
# Create a router
router = APIRouter(
    prefix="/pages",
    tags=["Frontend Pages"]
)

# Вказуємо FastAPI, де шукати HTML-шаблони
# Важливо: шлях вказується відносно кореня проєкту, де ви запускаєте uvicorn
# Tell FastAPI where to look for HTML templates
# Important: the path is specified relative to the root of the project where you run uvicorn
templates = Jinja2Templates(directory="src/car_qr_service/templates")


@router.get("/",
            response_class=HTMLResponse,
            summary="Повертає головну сторінку пошуку автомобіля за державним номером реєстрації "
                    "(Returns the main page for searching for a car by license plate number)")
async def get_main_page(request: Request):
    """
    Цей ендпоінт віддає нашу головну HTML-сторінку.
    This endpoint returns our main HTML page.
    """
    # We simply render the index.html file and pass the request object into it
    # Ми просто рендеримо файл index.html і передаємо в нього об'єкт request
    return templates.TemplateResponse(request, "index.html")


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    """
    Serves the user login page.
    """
    return templates.TemplateResponse(request, "pages/login.html")


@router.post("/login", response_class=HTMLResponse)
async def handle_login(
        response: Response,
        db: Annotated[AsyncSession, Depends(get_db_session)],
        # FastAPI автоматично візьме дані з форми
        email: str = Form(..., alias="username"),
        password: str = Form(...),
):
    """
    Handles the login form submission.
    Authenticates the user, sets a cookie, and redirects to the cabinet.
    """
    user = await authenticate_user(email, password, db)
    if not user:
        # В майбутньому тут можна показувати повідомлення про помилку на сторінці логіну
        return RedirectResponse(
            url="/pages/login", status_code=status.HTTP_302_FOUND
        )

    # Якщо автентифікація успішна, створюємо токен
    access_token = create_access_token(data={"sub": user.email})

    # Створюємо відповідь-перенаправлення на сторінку кабінету
    response = RedirectResponse(
        url="/pages/cabinet", status_code=status.HTTP_302_FOUND
    )

    # Встановлюємо токен в cookie. httponly=True означає, що
    # JavaScript на клієнті не зможе отримати доступ до цього cookie,
    # що є важливим елементом безпеки.
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return response


@router.get("/cabinet", response_class=HTMLResponse)
async def get_cabinet_page(
        request: Request,
        # 1. Використовуємо нового "охоронця", який читає з cookie і може повернути None
        current_user: Annotated[
            Optional[User], Depends(get_current_user_from_cookie)
        ],
        db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Serves the user's personal cabinet page.
    Redirects to login page if user is not authenticated.
    """
    # 1. Додаємо перевірку: якщо користувача немає, робимо редірект
    if current_user is None:
        return RedirectResponse(
            url="/pages/login", status_code=status.HTTP_302_FOUND
        )

    # 2. Якщо все добре, зчитуємо з бази усі авта користувача і віддаємо сторінку
    # Отримуємо список авто поточного користувача
    user_cars = await cars_crud.get_user_cars(db, owner_id=current_user.id)

    context = {
        "request": request,
        "user": current_user,
        "cars": user_cars,  # Передаємо список авто в шаблон
    }
    return templates.TemplateResponse(request, "pages/cabinet.html", context)


@router.post("/cabinet/add-car", response_class=HTMLResponse)
async def handle_add_car(
        request: Request,
        current_user: Annotated[User, Depends(get_current_user_from_cookie)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
        license_plate: str = Form(...),
        brand: str = Form(...),
        model: str = Form(...),
):
    """
    Handles the "Add Car" form submission via HTMX.
    """
    if not current_user:
        return HTMLResponse(content="Not authorized", status_code=401)

    car_data = CarCreate(license_plate=license_plate, brand=brand, model=model)
    new_car = await cars_crud.create_car(db=db, car=car_data, owner_id=current_user.id)

    context = {"request": request, "car": new_car}
    return templates.TemplateResponse(request, "partials/car_row.html", context)


@router.get("/qr-code/{license_plate}")
async def generate_qr_code(
        license_plate: str,
        current_user: Annotated[User, Depends(get_current_user_from_cookie)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Generates a QR code image for a specific car.
    Only the owner can generate the QR code.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    car = await cars_crud.get_car_by_license_plate(db, license_plate)

    if not car or car.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your car")

    # Формуємо URL для публічної сторінки
    # В реальному житті тут має бути ваш домен
    public_url = f"https://car-qr-service.onrender.com/pages/cars/{car.id}"

    # Генеруємо QR-код
    qr_img = qrcode.make(public_url)

    # Зберігаємо зображення в буфер в пам'яті
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    # Повертаємо зображення
    return StreamingResponse(buffer, media_type="image/png")


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    """
    Віддає сторінку реєстрації користувача.
    """
    return templates.TemplateResponse(request, "pages/register.html")


@router.post("/register")
async def handle_registration(
        db: Annotated[AsyncSession, Depends(get_db_session)],
        email: str = Form(...),
        phone_number: str = Form(...),
        password: str = Form(...),
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        show_phone_number: bool = Form(False),
):
    """
    Обробляє дані з форми реєстрації.
    Створює нового користувача і автоматично логінить його.
    """
    existing_user = await users_crud.get_user_by_email(email, db)
    if existing_user:
        # В реальному додатку тут варто показувати повідомлення про помилку
        return RedirectResponse(
            url="/pages/register?error=exists", status_code=status.HTTP_302_FOUND
        )

    user_data = UserCreate(
        email=email,
        phone_number=phone_number,
        password=password,
        first_name=first_name or "",
        last_name=last_name or "",
        show_phone_number=show_phone_number,
    )

    user = await users_crud.create_user(user_data, db)

    # Автоматично логінимо нового користувача
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(
        url="/pages/cabinet", status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return response


@router.delete("/cabinet/cars/{car_id}", response_class=HTMLResponse)
async def delete_car_for_user(
    car_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Handles deleting a car for the current user via HTMX.
    Returns an empty response to remove the row from the table.
    """
    if current_user is None:
        # User is not authenticated
        return HTMLResponse(status_code=status.HTTP_401_UNAUTHORIZED)
    # Find the car in the database
    car_to_delete = await cars_crud.get_car_by_id(db, car_id=car_id)
    # Check if the car exists and if it belongs to the current user
    if not car_to_delete or car_to_delete.owner_id != current_user.id:
        # Do not let the user know if the car exists or not, just forbid the action
        return HTMLResponse(status_code=status.HTTP_403_FORBIDDEN)
    # Delete the car
    await cars_crud.delete_car(db, car=car_to_delete)
    # Return an empty response, HTMX will replace the table row with it
    return HTMLResponse(content="", status_code=status.HTTP_200_OK)