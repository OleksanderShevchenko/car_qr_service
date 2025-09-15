from fastapi import FastAPI

from src.car_qr_service.users.router import router as users_router
from src.car_qr_service.auth.router import router as login_user
from src.car_qr_service.cars.router import router as car_router
from src.car_qr_service.public.router import router as public_router
from src.car_qr_service.pages.router import router as pages_router


app = FastAPI(title="Car QR Service",
              description="Service to contact with car owner by means of QR code.",
              version="0.0.1")
# include routers
app.include_router(users_router)
app.include_router(login_user)
app.include_router(car_router)
app.include_router(public_router)
app.include_router(pages_router)


@app.get("/")
def get_root():
    """
    Starting root end point
    """
    return {"message": "Hello, QR Car Service!"}
