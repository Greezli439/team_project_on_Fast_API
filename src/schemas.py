from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, EmailStr

from fastapi import File, Path

from src.database.models import Role


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=16)


class UserModel(UserBase):
    role: Role = Field()

class UserUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    role : Role
    information: str
   

class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    username: UserDb
    detail: str = "User successfully created"


class UserBan(BaseModel):
    user_id: int
    banned: bool = True


class UserChangeRole(BaseModel):
    user_id: int
    role: Role


class UserDBBanned(UserDb):
    banned: bool


class UserDBRole(UserDb):
    role: Role


####################################TAG###############################
class TagModel(BaseModel):
    name_tag: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int
    name_tag: str


    class Config:
        orm_mode = True


#################################TOKEN###############################
class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    access_token: str
    token_type: str

#################################COMMENT####################################
class CommentDeleteResponse(BaseModel):
    id: int = 1
    comment: str = 'My comment'

    class Config:
        orm_mode = True


class CommentResponse(BaseModel):
    id: int = 1
    comment: str
    username: UserDb
    image_id: int = 1

    class Config:
        orm_mode = True


class CommentModel(BaseModel):
    comment: str = Field(min_length=1, max_length=255)
    image_id: int = Field(1, gt=0)

class CommentModelUpdate(BaseModel):
    comment: str = Field(min_length=1, max_length=255)
    comment_id: int = Path(ge=1)

######################################IMAGE#############################
class ImageAddModel(BaseModel):
    description: str = Field(max_length=500)
    tags: Optional[List[str]]


class ImageAddTagModel(BaseModel):
    tags: Optional[List[str]]



class ImageDb(BaseModel):
    id: int
    url: str
    public_id: str
    image_name: str
    description: str
    tags: List[TagResponse]
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        exclude = {'updated_at', 'user', 'title'}





class ImageChangeSizeModel(BaseModel):
    id: int
    width: int = 200
    

class ImageChangeColorModel(BaseModel):
    id: int
    object: str 
    color: str


class ImageTransformModel(BaseModel):
    id: int


class ImageSignModel(BaseModel):
    id: int
    text: str

#GET
######################################IMAGE#############################
class ImageGetResponse(BaseModel):
    url: str
    description: str
    tags: List[TagResponse]
    comments: List[CommentResponse]


class ImageGetAllResponse(BaseModel):
    images_response: List[ImageGetResponse]


class GetQRCode(BaseModel):
    id: int
    base64_encoded_img: str


######################################IMAGE#############################

class ImageAddResponse(BaseModel):
    image: ImageDb
    detail: str = "Image has been added"

    class Config:
        orm_mode = True


class ImageAddTagResponse(BaseModel):
    id: int
    tags: List[TagResponse]
    detail: str = "Image tag has been updated"

    class Config:
        orm_mode = True


class ImageDeleteResponse(BaseModel):
    image: ImageDb
    detail: str = "Image has been deleted"


class ImageUpdateDescrResponse(BaseModel):
    id: int
    description: str
    detail: str = "Image has been updated"

    class Config:
        orm_mode = True


class ImageUpdateModel(BaseModel):
    description: str = Field(max_length=500)

class ImageNameUpdateModel(BaseModel):
    image_name: str

class ImageNameUpdateResponse(BaseModel):
    image: ImageDb
    detail: str = "Image has been added"

class ImageUpdateModel(BaseModel):
    description: str = Field(max_length=500)

######################################IMAGE#############################

