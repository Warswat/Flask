from typing import Optional, Type

import pydantic
from pydantic import BaseModel


class BaseUser(BaseModel):
    name: Optional[str]
    password: Optional[str]

    @pydantic.field_validator("password")
    @classmethod
    def secure_password(cls, value):
        if len(value) < 8:
            raise ValueError("password is too short")
        return value


class BaseAd(BaseModel):
    title: Optional[str]
    description: Optional[str]
    owner_id: Optional[int]


class CreateUser(BaseUser):

    name: str
    password: str


class CreateAd(BaseAd):

    title: Optional[str]
    description: Optional[str]
    owner_id: int


class UpdateUser(BaseUser):

    name: Optional[str]
    password: Optional[str]


class UpdateAd(BaseAd):

    title: Optional[str]
    description: Optional[str]


Schema = Type[CreateUser] | Type[UpdateUser]
