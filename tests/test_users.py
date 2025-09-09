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


def test_login_for_access_token_success(client: TestClient):
    """
    Test for successful obtain token.
    """
    # --- Arrange ---
    # 1. First we need to add new authorized user.
    user_data = {
        "email": "auth_test@example.com",
        "phone_number": "+380997654321",
        "password": "correct_password",
        "first_name": "Auth",
        "last_name": "Test",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201, "Error to create new test user"

    # 2. Prepare data for LogIn.
    #    IMPORTANT: OAuth2 "password flow" expects data in format form-data,
    #    not a JSON. TestClient automatically made this if we pass data in argument data, not json.
    login_data = {
        "username": user_data["email"],  # field calls 'username' according standard
        "password": user_data["password"],
    }

    # --- Act 1(getting token) ---
    # Send request to get token
    response = client.post("/auth/token", data=login_data)

    # --- Assert (Check results) ---
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]  # <-- Зберігаємо токен у змінну

    # --- Act 2 (Get current user with token) ---
    # Create authorization header,  as it is expected by the end point 'users/me'.
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    # make request to protected endpoint, adding the header to request.
    response_me = client.get("/users/me", headers=headers)

    # --- Assert (Check results) ---
    assert response_me.status_code == 200, f"Отримано помилку: {response_me.text}"
    current_user_data = response_me.json()
    assert current_user_data["email"] == user_data["email"]
    assert current_user_data["first_name"] == user_data["first_name"]


def test_login_for_access_token_failure_wrong_password(client: TestClient):
    """
    Test for unsuccessful authorization.
    """
    # --- Arrange ---
    # 1. First we need to add new authorized user.
    user_data = {
        "email": "auth_fail_test@example.com",
        "phone_number": "+380991112233",
        "password": "correct_password",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    # 2. Prepare data for LogIn.
    # Use incorrect password
    login_data = {
        "username": user_data["email"],
        "password": "WRONG_password",
    }

    # --- 3. Act (Try to get token) ---
    response = client.post("/auth/token", data=login_data)

    # --- 4. Assert (Check results) ---
    # Очікуємо статус 401 Unauthorized
    assert response.status_code == 401
    error_data = response.json()
    assert error_data["detail"] == "Incorrect email or password"

    # 5. Prepare data for LogIn.
    # Use incorrect username
    login_data = {
        "username": "auth_fail_test2@example.com",
        "password": user_data["password"],
    }

    # --- 6. Act (Try to get token) ---
    response = client.post("/auth/token", data=login_data)

    # --- 7. Assert (Check results) ---
    # Очікуємо статус 401 Unauthorized
    assert response.status_code == 401
    error_data = response.json()
    assert error_data["detail"] == "Incorrect email or password"
