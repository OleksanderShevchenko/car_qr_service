import pytest

from fastapi.testclient import TestClient


# pytest will automatically find our fixture client from conftest.py
# There is no needs to import something
def test_create_user(client: TestClient):
    # prepare user data as dict - jsonlike
    user_data = {"email": "test@example.com",
        "phone_number": "+380991234567",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",}

    # 2. add user
    response = client.post("/users/", json=user_data)

    # 3. Assert results
    assert response.status_code == 201, response.text
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert response_data["first_name"] == user_data["first_name"]
    assert "id" in response_data
    # check that the password has not been returned in response
    assert "password" not in response_data
    assert "hashed_password" not in response_data