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
