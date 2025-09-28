import datetime
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.security import verify_password
from src.car_qr_service.config import settings
from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.database.models import User
from src.car_qr_service.users import crud as users_crud

# Create schema OAuth2.
# tokenUrl pointing to endpoint, where the client can get token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(email: str,
                            password: str,
                            db: AsyncSession) -> User | bool:
    """
    Authenticate a user by email and password.
    """
    user = await users_crud.get_user_by_email(email, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# --- ОХОРОНЕЦЬ №1: ДЛЯ JSON API ---
# Він вимагає токен в заголовку і кидає помилку HTTPException.
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Annotated[AsyncSession, Depends(get_db_session)]) -> User:
    """
    Отримує поточного користувача з токена JWT у заголовку авторизації.
    Підвищує httpexception, якщо автентифікація не вдається.
    Використовується для кінцевих точок API.
    Gets the current user from the JWT token in the Authorization header.
    Raises HTTPException if authentication fails.
    Used for API endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося перевірити облікові дані",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,
                             settings.JWT_SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await users_crud.get_user_by_email(email, db)
    if user is None:
        raise credentials_exception
    return user


# --- ОХОРОНЕЦЬ №2: ДЛЯ ВЕБ-СТОРІНОК ---
# Він читає токен з cookie і повертає None, якщо щось не так.
async def get_current_user_from_cookie(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """
    Gets the current user from the JWT token stored in the browser cookie.
    Returns None if the user is not authenticated.
    Used for web page endpoints that need redirection.
    """
    access_token = request.cookies.get("access_token")

    if not access_token:
        return None

    try:
        scheme, _, param = access_token.partition(" ")
        if scheme.lower() != "bearer":
            return None

        payload = jwt.decode(
            param, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = await users_crud.get_user_by_email(email=email, db=db)
    return user
