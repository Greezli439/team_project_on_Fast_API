from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import File


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=16)


class UserModel(UserBase):
    role: str = Field()


class UserDb(BaseModel):
    id: int
    username: str = "Jack"
    email: str = "jacck@jack.com"
    created_at: datetime

    # avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    username: UserDb
    detail: str = "User successfully created"


class TagModel(BaseModel):
    name_tag: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int = 1
    name_tag: str

    class Config:
        orm_mode = True


class ImageBase(BaseModel):
    username: str
    id: int
    title: str
    url: str
    created_at: datetime


class ImageModel(ImageBase):
    tags: List[int]


class ImageResponse(ImageBase):
    user: UserDb
    id: int
    tags: List[TagResponse]


class CommentDeleteResponse(BaseModel):
    id: int = 1
    comment: str = 'My comment'

    class Config:
        orm_mode = True


#
class CommentResponse(BaseModel):
    id: int = 1
    comment: str
    username: UserDb
    image_id: int = 1

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class CommentModel(BaseModel):
    id: int
    comment: str = Field(min_length=1, max_length=255)
    user_id: int = Field(1, gt=0)
    image_id: int = Field(1, gt=0)
