import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status, Cookie
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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Annotated[AsyncSession, Depends(get_db_session)]) -> User:
    """
    dependence function to get current user by JWT-token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося перевірити облікові дані",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await users_crud.get_user_by_email(email, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_from_cookie(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Reads and validates the JWT token from the browser's cookie.
    """
    if access_token is None:
        # Якщо cookie немає, перенаправляємо на сторінку входу
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Not authenticated",
            headers={"Location": "/pages/login"},
        )

    # Токен з cookie містить "Bearer ", прибираємо це
    token = access_token.split(" ")[-1]

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

    user = await users_crud.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
