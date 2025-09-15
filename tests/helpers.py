from starlette.testclient import TestClient


def get_auth_token(client: TestClient, user_suffix: str = "") -> str:
    """Допоміжна функція для створення користувача та отримання токену."""
    user_data = {
        "email": f"car_test{user_suffix}@example.com",
        "phone_number": f"+380991234567{user_suffix}",  # Ensure unique phone numbers
        "password": "testpassword",
    }
    # Створюємо користувача (ігноруємо відповідь, якщо він вже існує)
    client.post("/users/", json=user_data)

    # Отримуємо токен
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


def create_car_for_user(client: TestClient, token: str, car_suffix: str = "") -> dict:
    """Допоміжна функція для створення авто та повернення його даних."""
    headers = {"Authorization": f"Bearer {token}"}
    car_data = {
        "license_plate": f"PLATE-{car_suffix}",
        "brand": f"Brand-{car_suffix}",
        "model": f"Model-{car_suffix}",
    }
    response = client.post("/cars/", json=car_data, headers=headers)
    assert response.status_code == 201
    return response.json()
