from pydantic import BaseModel, Field


class CommentModel(BaseModel):
    comment: str = Field(min_length=1, max_length=255)
    user_id: int = Field(1, gt=0)
    image_id: int = Field(1, gt=0)


class CommentResponse(BaseModel):
    id: int = 1
    comment: str = 'placeholder comment'
    user: UserResponse  # To be changed when User done
    image_id: int = 1

    class Config:
        orm_mode = True


class CommentDeleteResponse(BaseModel):
    id: int = 1
    comment: str = 'placeholder comment'

    class Config:
        orm_mode = True
