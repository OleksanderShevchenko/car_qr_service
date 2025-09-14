from fastapi.testclient import TestClient


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


def test_create_car_success(client: TestClient):
    """Тест успішного створення автомобіля для авторизованого користувача."""
    token = get_auth_token(client, user_suffix="1")
    headers = {"Authorization": f"Bearer {token}"}
    car_data = {
        "license_plate": "AO1234BC",
        "brand": "Toyota",
        "model": "Camry",
    }
    response = client.post("/cars/", json=car_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["license_plate"] == car_data["license_plate"]


def test_create_car_unauthorized(client: TestClient):
    """Тест на помилку при спробі створити авто без токену."""
    car_data = {
        "license_plate": "AE5678BH",
        "brand": "BMW",
        "model": "X5",
    }
    response = client.post("/cars/", json=car_data)
    assert response.status_code == 401


# --- Тести для отримання списку авто ---

def test_get_my_cars_with_two_cars(client: TestClient):
    """Тест: користувач має два авто і отримує список з двох авто."""
    # Arrange: Створюємо користувача і додаємо йому два авто
    token = get_auth_token(client, user_suffix="2")
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/cars/", json={"license_plate": "CAR001", "brand": "A", "model": "1"}, headers=headers
    )
    client.post(
        "/cars/", json={"license_plate": "CAR002", "brand": "B", "model": "2"}, headers=headers
    )

    # Act: Робимо запит на отримання списку
    response = client.get("/cars/", headers=headers)

    # Assert: Перевіряємо, що отримали 2 авто
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_my_cars_with_one_car(client: TestClient):
    """Тест: користувач має одне авто і отримує список з одного авто."""
    # Arrange: Створюємо користувача і додаємо йому одне авто
    token = get_auth_token(client, user_suffix="3")
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/cars/", json={"license_plate": "CAR003", "brand": "C", "model": "3"}, headers=headers
    )

    # Act: Робимо запит
    response = client.get("/cars/", headers=headers)

    # Assert: Перевіряємо, що отримали 1 авто
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["license_plate"] == "CAR003"


def test_get_my_cars_with_no_cars(client: TestClient):
    """Тест: користувач не має авто і отримує порожній список."""
    # Arrange: Створюємо нового користувача без авто
    token = get_auth_token(client, user_suffix="4")
    headers = {"Authorization": f"Bearer {token}"}

    # Act: Робимо запит
    response = client.get("/cars/", headers=headers)

    # Assert: Перевіряємо, що список порожній
    assert response.status_code == 200
    assert response.json() == []


def test_get_my_cars_does_not_show_other_users_cars(client: TestClient):
    """Тест: користувач не бачить автомобілі інших користувачів."""
    # Arrange: Створюємо двох користувачів. Першому додаємо авто.
    token_user_1 = get_auth_token(client, user_suffix="5")
    token_user_2 = get_auth_token(client, user_suffix="6")

    headers_user_1 = {"Authorization": f"Bearer {token_user_1}"}
    client.post(
        "/cars/", json={"license_plate": "CAR_USER1", "brand": "D", "model": "4"}, headers=headers_user_1
    )

    # Act: Другий користувач (у якого немає авто) робить запит на отримання списку.
    headers_user_2 = {"Authorization": f"Bearer {token_user_2}"}
    response = client.get("/cars/", headers=headers_user_2)

    # Assert: Перевіряємо, що другий користувач отримав порожній список.
    assert response.status_code == 200
    assert response.json() == []

