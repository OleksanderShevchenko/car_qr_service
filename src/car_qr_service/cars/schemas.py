from typing import Optional

from pydantic import BaseModel, ConfigDict


class CarBase(BaseModel):
    """Базова схема для автомобіля."""
    license_plate: str
    brand: str
    model: str


class CarCreate(CarBase):
    """Схема для створення нового автомобіля (вхідні дані)."""
    pass


class CarRead(CarBase):
    """Схема для читання даних про автомобіль (вихідні дані)."""
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class CarUpdate(BaseModel):
    """
    Схема для оновлення автомобіля. Всі поля опціональні.
    """

    license_plate: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PublicCarInfo(BaseModel):
    """
    Схема для публічної інформації про автомобіль.
    Показує тільки безпечні дані (марка та модель).
    """
    brand: str
    model: str

    model_config = ConfigDict(from_attributes=True)

