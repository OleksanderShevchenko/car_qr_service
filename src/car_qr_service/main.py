from fastapi import FastAPI

from src.car_qr_service.users.router import router as users_router


app = FastAPI(title="Car QR Service",
              description="Service to contact with car owner by means of QR code.",
              version="0.0.1")
# include routers
app.include_router(users_router)

@app.get("/")
def get_root():
    """
    Starting root end point
    """
    return {"message": "Hello, QR Car Service!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=8101)