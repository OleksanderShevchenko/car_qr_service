from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Request, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import get_current_user, authenticate_user, create_access_token, \
    get_current_user_from_cookie
from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.database.models import User

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
    # Ця залежність захищає ендпоінт. Якщо користувач не залогінений,
    # він отримає помилку 401. Ми покращимо це пізніше.
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
):
    """
    Віддає сторінку особистого кабінету.
    Доступно тільки для автентифікованих користувачів.
    """
    # Передаємо об'єкт користувача в шаблон, щоб показати його ім'я
    context = {"request": request, "user": current_user}
    return templates.TemplateResponse(request, "pages/cabinet.html", context)
