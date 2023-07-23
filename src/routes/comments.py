from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.database.models import Image, User

from src.repository import users as repository_users

from src.schemas import UserModel, UserResponse, TokenModel, ImageBase, ImageResponse, CommentResponse, CommentModel, \
    CommentDeleteResponse
from src.repository import comments as repository_comments

# from src.services.auth import auth_service

router = APIRouter(prefix='/comments', tags=["comments"])

security = HTTPBearer()


# заменить на авторизированого пользователя
@router.get('/', response_model=List[CommentResponse])
async def get_comments(db: Session = Depends(get_db)):
    comments = await repository_comments.get_comments(db)
    return comments


@router.get('/{comment_id}', response_model=CommentResponse)
async def get_comment_by_id(comment_id: int = Path(ge=1), db: Session = Depends(get_db)):
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment


@router.post('/', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentModel, db: Session = Depends(get_db)):
    try:
        image = db.query(Image).filter_by(id=body.image_id).first()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such image")
    # body.user_id = current_user.id
    comment = await repository_comments.create_comment(body, db)
    return comment


@router.put('/{comment_id}', response_model=CommentResponse)
async def update_comment(body: CommentModel, comment_id: int = Path(ge=1), db: Session = Depends(get_db)):
    comment = await repository_comments.update_comment(body, comment_id, db)
    return comment


@router.delete('/{comment_id}', response_model=CommentDeleteResponse)
async def remove_comment(comment_id: int = Path(ge=1), db: Session = Depends(get_db)):
    comment = await repository_comments.remove_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment
