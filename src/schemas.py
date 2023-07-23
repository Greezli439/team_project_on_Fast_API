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
    username: str
    email: str
    created_at: datetime
    # avatar: str


    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int
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


class CommentRequest(BaseModel):
    image_id: int


class CommentBase(BaseModel):
    comment: str

class CommentResponse(CommentsBase):
    # username: str
    user_id: int
    updated_at: datetime

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class CommentModel(BaseModel):
    comment: str = Field(min_length=1, max_length=255)
    user_id: int = Field(1, gt=0)
    image_id: int = Field(1, gt=0)

