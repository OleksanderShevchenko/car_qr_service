
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.database.database import get_db_session
from src.car_qr_service.users import crud
from src.car_qr_service.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Here we are creating new user and return his/her data."
)
async def create_new_user(
    body: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint for registration of a new user.
    - **body**: data of the new user.
    - **db**: database session to work with database (obtained though Dependency Injection from function).
    """
    # First check if a user with same email already exists
    existing_user = await crud.get_user_by_email(body.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {body.email} already exists."
        )

    # All right - creat new user
    new_user = await crud.create_user(body, db)
    return new_user
