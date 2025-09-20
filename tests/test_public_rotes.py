import asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Імпортуємо допоміжні функції з централізованого файлу
from tests.helpers import create_car_for_user, get_auth_token


def test_find_car_by_plate_success(client: TestClient, db_session: AsyncSession):
    """Test: successful search for existing auto by its  license plate."""
    # Arrange: Create new user and add him auto
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
    license_plate = data["license_plate"]
    # force to store new car in the database
    asyncio.run(db_session.commit())

    # Act: Робимо публічний запит до нового endpoint-у
    response = client.get(f"/public/cars/{license_plate}")

    # Assert: Перевіряємо, що авто знайдено і повернуто правильні дані
    assert response.status_code == 200
    public_info = response.json()
    assert public_info["brand"] == car_data["brand"]
    assert public_info["model"] == car_data["model"]
    # check that public data has no extra information we are not intend to show
    assert "id" not in public_info
    assert "owner_id" not in public_info
    assert "license_plate" not in public_info


def test_find_car_by_plate_not_found(client: TestClient, db_session: AsyncSession):
    """Test: unsuccessful search for existing auto by its  license plate."""
    # Arrange: Create new user and add him auto
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
    license_plate = data["license_plate"]
    # force to store new car in the database
    asyncio.run(db_session.commit())

    # Act: Робимо публічний запит до нового endpoint-у
    response = client.get(f"/public/cars/AO1234BО")  # change one letter in the license plate
    assert response.status_code == 404


def test_find_car_by_plate_hides_phone_by_default(
        client: TestClient, db_session: AsyncSession
):
    """
    Test: Search for a car whose owner has hidden the phone number.
    The number should not be displayed in the HTML response.
    """
    # Arrange: Створюємо користувача, який НЕ хоче показувати свій номер (за замовчуванням)
    user_suffix = "public_hide"
    token = get_auth_token(client, user_suffix=user_suffix, show_phone=False)
    car_data = create_car_for_user(client, token, car_suffix="H01")
    license_plate = car_data["license_plate"]

    # Потрібно закомітити транзакцію, щоб зробити дані видимими для наступного запиту
    asyncio.run(db_session.commit())

    # Act: Робимо запит до HTMX-ендпоінту, передаючи дані як форма
    response = client.post("/public/search", data={"license_plate": license_plate})

    # Assert: Перевіряємо, що авто знайдено, а номер телефону прихований
    assert response.status_code == 200
    assert "Власник приховав номер" in response.text
    assert f"+380991234567{user_suffix}" not in response.text


def test_find_car_by_plate_shows_phone_when_allowed(
        client: TestClient, db_session: AsyncSession
):
    """
    Test: Search for a car whose owner has allowed showing the phone number.
    The number should be displayed in the HTML response.
    """
    # Arrange: Створюємо користувача, який ХОЧЕ показувати свій номер
    user_suffix = "public_show"
    token = get_auth_token(client, user_suffix=user_suffix, show_phone=True)
    car_data = create_car_for_user(client, token, car_suffix="S01")
    license_plate = car_data["license_plate"]

    # Потрібно закомітити транзакцію, щоб зробити дані видимими для наступного запиту
    asyncio.run(db_session.commit())

    # Act: Робимо запит до HTMX-ендпоінту, передаючи дані як форма
    response = client.post("/public/search", data={"license_plate": license_plate})

    # Assert: Перевіряємо, що авто знайдено, а номер телефону видимий
    assert response.status_code == 200
    assert "Власник приховав номер" not in response.text
    assert f"+380991234567{user_suffix}" in response.text


def test_find_car_by_plate_not_found_htmx(client: TestClient):
    """Test: Searching for a non-existent car via HTMX returns a special message."""
    response = client.post("/public/search", data={"license_plate": "NONEXISTENT"})
    assert response.status_code == 200  # HTMX endpoint always returns 200 OK
    assert "Автомобіль з таким номером не знайдено" in response.text
