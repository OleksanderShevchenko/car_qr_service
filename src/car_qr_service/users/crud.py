
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.car_qr_service.auth.security import hash_password
from src.car_qr_service.database.models import User
from src.car_qr_service.users.schemas import UserCreate


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """Get user from database by its email."""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(id: int, db: AsyncSession) -> User | None:
    """Get user from database by its id."""
    query = select(User).where(User.id == id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_phone(phone_number: str, db: AsyncSession) -> User | None:
    """Get user from database by its phone_number."""
    query = select(User).where(User.phone_number == phone_number)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user(body: UserCreate, db: AsyncSession) -> User:
    """Create new user in the database"""
    # Create instance of User class
    new_user = User(
        email=body.email,
        phone_number=body.phone_number,
        first_name=body.first_name,
        last_name=body.last_name,
        # Важливо: хешуємо пароль перед збереженням!
        hashed_password=hash_password(body.password),
        show_phone_number = body.show_phone_number,
    )
    # Add new user in database session
    db.add(new_user)
    # commit changes into physical database - to file
    await db.commit()
    # Update new_user object with data from database (for example id)
    await db.refresh(new_user)
    return new_user