import datetime

from sqlalchemy import String, ForeignKey, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.car_qr_service.database.database import Base


class User(Base):
    """
    Модель Користувача.
    Представляє таблицю 'users' в базі даних.
    User Model.
    Represents the 'users' table in the database.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    first_name: Mapped[str] = mapped_column(String(128),default="", server_default="")
    last_name: Mapped[str] = mapped_column(String(128), default="", server_default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc), server_default=func.now()
    )
    show_phone_number: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    # Зв'язок "один-до-багатьох": один користувач може мати багато автомобілів.
    # back_populates="owner" вказує на атрибут 'owner' в моделі Car.
    # One-to-many relationship: one user can have many cars.
    # back_populates="owner" points to the 'owner' attribute in the Car model.
    cars: Mapped[list["Car"]] = relationship(back_populates="owner")


class Car(Base):
    """
    Модель Автомобіля.
    Представляє таблицю 'cars' в базі даних.
    Car Model.
    Represents the 'cars' table in the database.
    """
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    license_plate: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # Зв'язок "багато-до-одного": багато авто можуть належати одному користувачу.
    # back_populates="cars" вказує на атрибут 'cars' в моделі User.
    # Many-to-one relationship: many cars can belong to the same user.
    # back_populates="cars" points to the 'cars' attribute in the User model.
    owner: Mapped["User"] = relationship(back_populates="cars")
