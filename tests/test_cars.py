from fastapi.testclient import TestClient

from helpers import get_auth_token, create_car_for_user


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


# --- Тести для оновлення ---
def test_update_my_car_success(client: TestClient):
    """Тест: користувач успішно оновлює свій автомобіль."""
    token = get_auth_token(client, "update01")
    car = create_car_for_user(client, token, "U01")
    car_id = car["id"]
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {"license_plate": "NEW-PLATE"}
    response = client.patch(f"/cars/{car_id}", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["license_plate"] == "NEW-PLATE"
    assert data["brand"] == car["brand"]


def test_update_other_user_car_forbidden(client: TestClient):
    """Тест: користувач не може оновити автомобіль іншого користувача."""
    token1 = get_auth_token(client, "update02")
    token2 = get_auth_token(client, "update03")
    car = create_car_for_user(client, token1, "U02")
    car_id = car["id"]

    headers_user2 = {"Authorization": f"Bearer {token2}"}
    update_data = {"license_plate": "HACKED"}
    response = client.patch(f"/cars/{car_id}", json=update_data, headers=headers_user2)
    assert response.status_code == 403


# --- Тести для видалення ---
def test_delete_one_of_multiple_cars(client: TestClient):
    """Тест: у користувача є кілька авто, він видаляє одне, і список оновлюється."""
    # Arrange: Створюємо користувача і додаємо йому ДВА авто
    token = get_auth_token(client, "del01")
    headers = {"Authorization": f"Bearer {token}"}
    car1 = create_car_for_user(client, token, "D01A")
    create_car_for_user(client, token, "D01B")
    car_to_delete_id = car1["id"]

    # Перевіряємо, що в користувача справді 2 авто
    response_get = client.get("/cars/", headers=headers)
    assert len(response_get.json()) == 2

    # Act: Видаляємо одне з авто
    response_delete = client.delete(f"/cars/{car_to_delete_id}", headers=headers)
    assert response_delete.status_code == 204

    # Assert: Перевіряємо, що в списку залишилось тільки одне авто
    response_get_after = client.get("/cars/", headers=headers)
    assert response_get_after.status_code == 200
    cars_after = response_get_after.json()
    assert len(cars_after) == 1
    assert cars_after[0]["id"] != car_to_delete_id


def test_delete_other_user_car_forbidden(client: TestClient):
    """Тест: користувач не може видалити автомобіль іншого користувача."""
    token1 = get_auth_token(client, "del02")
    token2 = get_auth_token(client, "del03")
    car = create_car_for_user(client, token1, "D02")
    car_id = car["id"]

    headers_user2 = {"Authorization": f"Bearer {token2}"}
    response = client.delete(f"/cars/{car_id}", headers=headers_user2)
    assert response.status_code == 403

    # Переконуємось, що авто не було видалено
    headers_user1 = {"Authorization": f"Bearer {token1}"}
    response_get = client.get("/cars/", headers=headers_user1)
    assert len(response_get.json()) == 1

