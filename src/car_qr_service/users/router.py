from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.utils import get_current_user
from src.car_qr_service.database.models import User

from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.users import crud
from src.car_qr_service.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створюємо нового користувача. (Create new user)",
)
async def create_new_user(
    body: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    """
    Кінцева точка для реєстрації нового користувача.
    - **body**: дані нового користувача.
    - **db**: сеанс бази даних для роботи з базою даних (отримано через Dependency Injection з функції).

    Endpoint for registration of a new user.
    - **body**: data of the new user.
    - **db**: database session to work with database (obtained though Dependency Injection from function).
    """
    # Спочатку перевіряю, чи вже існує користувач із такою ж електронною поштою.
    # First check if a user with same email already exists
    try:
        new_user = await crud.create_user(body, db)
        return new_user

    except IntegrityError as e:
        # Якщо база повернула помилку унікальності (дублікат)
        await db.rollback()  # Обов'язково відкочуємо сесію

        # Перевіряємо текст помилки, щоб зрозуміти, що саме дублюється
        # (Postgres зазвичай пише це в e.orig)
        error_msg = str(e.orig)

        if "users_email_key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {body.email} already exists."
            )
        elif "users_phone_number_key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with phone {body.phone_number} already exists."
            )
        else:
            # Якась інша помилка бази
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error"
            )
    except ValidationError as err:
        if "password" in str(err):
            # Некоректний пароль
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incorrect password! Details: {err}"
            )
        else:
            #  Якась інша помилка валідації
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {err}"
            )


@router.get("/me",
            response_model=UserRead,
            summary="Отримати дані поточного користувача. (Get data of current user)")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Повертає дані про користувача, який зараз залогінений.
    Доступ можливий тільки з валідним JWT-токеном.
    Returns data about the currently logged in user.
    Access is only possible with a valid JWT token.
    """
    return current_user
