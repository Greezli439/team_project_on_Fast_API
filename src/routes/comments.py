from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.schemas import UserModel, UserResponse, TokenModel, ImageBase, ImageResponse, CommentsBase, CommentsResponce, CommentModel
from src.repository import comments as repository_comments
# from src.services.auth import auth_service

router = APIRouter(prefix='/comments', tags=["comments"])

security = HTTPBearer()

#заменить на авторизированого пользователя
@router.post('/edit/{comment_id}', response_model=CommentsResponce)
async def edit_comment_by_id(body: CommentModel,
                             db: Session = Depends(get_db)):
    comment = await repository_comments.update_comment(body, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.post('/{image_id}', response_model=CommentsResponce)
async def add_new_comments(body: CommentModel,
                           db: Session = Depends(get_db)):
    comment = repository_comments.create_comment(body, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.get('/{image_id}', response_model=List[CommentsResponce])
async def get_comments_for_photo(body: CommentModel,
                                    db: Session = Depends(get_db)):
    comments = repository_comments.get_comments_for_photo(body, db)
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comments

@router.delete('/{comment_id}')
async def remove_comment(comment_id: int,
                         db: Session = Depends(get_db)):
    comment = repository_comments.remove_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
