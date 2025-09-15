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