from fastapi.testclient import TestClient


def get_auth_token(client: TestClient) -> str:
    """Допоміжна функція для створення користувача та отримання токену."""
    user_data = {
        "email": "car_test@example.com",
        "phone_number": "+380991234567",
        "password": "testpassword",
    }
    # Створюємо користувача (ігноруємо відповідь, якщо він вже існує)
    client.post("/users/", json=user_data)

    # Отримуємо токен
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_car_success(client: TestClient):
    """Тест успішного створення автомобіля для авторизованого користувача."""
    # --- Arrange ---
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    car_data = {
        "license_plate": "AO1234BC",
        "brand": "Toyota",
        "model": "Camry",
    }

    # --- Act ---
    response = client.post("/cars/", json=car_data, headers=headers)

    # --- Assert ---
    assert response.status_code == 201
    data = response.json()
    assert data["license_plate"] == car_data["license_plate"]
    assert data["brand"] == car_data["brand"]
    assert "id" in data
    assert "owner_id" in data


def test_create_car_unauthorized(client: TestClient):
    """Тест на помилку при спробі створити авто без токену."""
    # --- Arrange ---
    car_data = {
        "license_plate": "AE5678BH",
        "brand": "BMW",
        "model": "X5",
    }

    # --- Act ---
    # Робимо запит БЕЗ заголовку Authorization
    response = client.post("/cars/", json=car_data)

    # --- Assert ---
    assert response.status_code == 401
