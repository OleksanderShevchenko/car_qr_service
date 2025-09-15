from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Створюємо роутер
router = APIRouter(
    prefix="/pages",
    tags=["Frontend Pages"]
)

# Вказуємо FastAPI, де шукати HTML-шаблони
# Важливо: шлях вказується відносно кореня проєкту, де ви запускаєте uvicorn
templates = Jinja2Templates(directory="src/car_qr_service/templates")


@router.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request):
    """
    Цей ендпоінт віддає нашу головну HTML-сторінку.
    """
    # Ми просто рендеримо файл index.html і передаємо в нього об'єкт request
    return templates.TemplateResponse("index.html", {"request": request})
