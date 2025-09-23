from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import create_access_token, authenticate_user
from src.car_qr_service.database.database import get_db_session

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
    # Використовуємо нашу нову централізовану функцію
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
