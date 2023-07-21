from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.schemas import UserModel, UserResponse, TokenModel, ImageBase, ImageResponse, CommentsBase, CommentsResponce
from src.repository import users as repository_users
# from src.services.auth import auth_service

router = APIRouter(prefix='/comments', tags=["comments"])

security = HTTPBearer()

@router.post('/edit/{comment_id}', response_model=CommentsResponce)
async def edit_comment_for_id(comment: str,
                              comment_id: int,
                              db: Session = Depends(get_db)):
    pass


@router.post('/{image_id}', response_model=CommentsResponce)
async def add_new_comments(image_id: int,
                           db: Session = Depends(get_db)):
    pass


@router.get('/{image_id}', response_model=CommentsResponce)
async def get_images_comments_for_id(image_id: int,
                            db: Session = Depends(get_db)):
    pass