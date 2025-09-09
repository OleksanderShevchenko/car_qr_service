import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class BaseUser(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    phone_number: str
    first_name: str | None = None
    last_name: str | None = None


# Schema to create new user
# this king of data we are expecting in POST request
class UserCreate(BaseUser):
    password: Annotated[str, Field(min_length=8)]


# Schema to read data of existing user
# that what we expect to get in result of request
class UserRead(BaseUser):
    id: int
    created_at: datetime.datetime

    # This configuration allows Pydantic to read data
    # from SQLAlchemy objects - our model classes
    model_config = ConfigDict(from_attributes=True)
