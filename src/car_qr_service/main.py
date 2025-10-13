from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.car_qr_service.users.router import router as users_router
from src.car_qr_service.auth.router import router as login_user
from src.car_qr_service.cars.router import router as car_router
from src.car_qr_service.public.router import router as public_router
from src.car_qr_service.pages.router import router as pages_router, templates


app = FastAPI(title="Car QR Service",
              description="Service to contact with car owner by means of QR code.",
              version="0.0.1")

# Цей рядок каже FastAPI: "Якщо запит починається з /static,
# шукай відповідний файл у папці 'src/car_qr_service/static'".
app.mount("/static", StaticFiles(directory="src/car_qr_service/static"), name="static")

# include routers
app.include_router(users_router)
app.include_router(login_user)
app.include_router(car_router)
app.include_router(public_router)
app.include_router(pages_router)


@app.get("/",
            response_class=HTMLResponse,
            summary="Повертає головну вітальну сторінку яка відкривається для кореневої адреси "
                    "(Returns the main welcome page that opens for the root address)")
async def get_root(request: Request):
    """
    Цей ендпоінт віддає нашу головну вітальну HTML-сторінку.
    This endpoint returns our main welcoming HTML page.
    """
    # We simply render the pages/welcome.html file and pass the request object into it
    # Ми просто рендеримо файл pages/welcome.html і передаємо в нього об'єкт request
    return templates.TemplateResponse(request, "pages/welcome.html")
