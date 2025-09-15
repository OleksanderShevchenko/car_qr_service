from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import create_access_token
from src.car_qr_service.auth.security import verify_password
from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.users import crud

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token",
             summary="Повертає JWT токен для зареєстрованого користувача (Returns a token for a registered user)")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]):
    """
    Кінцева точка для отримання JWT-токена.
    Отримує електронну пошту як `ім'я користувача` та пароль.

    Endpoint for getting JWT-token.
    Gets email as `username` and password.
    """
    # 1. Знаходимо користувача за email (який передається в полі username)
    #    Find the user by email (which is passed in the username field)
    user = await crud.get_user_by_email(form_data.username, db)

    # 2. Якщо користувача не знайдено АБО пароль невірний, повертаємо помилку
    #    If the user is not found OR the password is incorrect, we return an error
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Створюємо JWT-токен
    #    Creating a JWT token
    access_token = create_access_token(data={"sub": user.email})

    # 4. Повертаємо токен
    #    Returning the token
    return {"access_token": access_token, "token_type": "bearer"}
