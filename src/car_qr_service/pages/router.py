from typing import Annotated, AsyncGenerator, Optional

from fastapi import APIRouter, Request, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import get_current_user, authenticate_user, create_access_token, \
    get_current_user_from_cookie
from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.database.models import User
from src.car_qr_service.users import crud as users_crud
from src.car_qr_service.users.schemas import UserCreate

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
):
    """
    Serves the user's personal cabinet page.
    Redirects to login page if user is not authenticated.
    """
    # 2. Додаємо перевірку: якщо користувача немає, робимо редірект
    if current_user is None:
        return RedirectResponse(
            url="/pages/login", status_code=status.HTTP_302_FOUND
        )

    # 3. Якщо все добре, віддаємо сторінку
    context = {"request": request, "user": current_user}
    return templates.TemplateResponse(request, "pages/cabinet.html", context)


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
