import datetime
from pydantic import BaseModel, EmailStr, Field


# Schema to create new user
# this king of data we are expecting in POST request
class UserCreate(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    # пароль має бути від 8 до 32 символів
    password: str = Field(..., min_length=8, max_length=32)


# Schema to read data of existing user
# that what we expect to get in result of request
class UserRead(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    created_at: datetime.datetime

    # This configuration allows Pydantic to read data
    # from SQLAlchemy objects - our model classes
    class Config:
        from_attributes = True
