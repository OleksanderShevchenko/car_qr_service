from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
