from fastapi import FastAPI


app = FastAPI(title="Car QR Service",
              description="Сервіс для зв'язку з власником авта через QR код.",
              version="0.0.1")


@app.get("/")
def get_root():
    """
    Starting root end point
    """
    return {"message": "Hello, QR Car Service!"}