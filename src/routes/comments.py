from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.database.models import User, Role
from src.schemas import UserModel, UserResponse, TokenModel, ImageBase, ImageResponse, CommentsBase, CommentsResponce
from src.repository import users as repository_users
from src.services.users import auth_service
from src.services.roles import RolesAccess

router = APIRouter(prefix='/comments', tags=["comments"])

security = HTTPBearer()

@router.post('/edit/{comment_id}', response_model=CommentsResponce)
async def edit_comment_for_id(comment: str,
                              comment_id: int,
                              db: Session = Depends(get_db),
                              current_user: User = Depends(
                                  auth_service.get_current_user)
                              ):
    pass


@router.post('/{image_id}', response_model=CommentsResponce)
async def add_new_comments(image_id: int,
                           db: Session = Depends(get_db)):
    pass


@router.get('/{image_id}', response_model=CommentsResponce)
async def get_images_comments_for_id(image_id: int,
                            db: Session = Depends(get_db)):
    pass


@router.delete('/{image_id}', response_model=ImageResponse,
               dependencies=[Depends(RolesAccess([Role.admin, Role.moderator]))])
async def remove_images_comments_for_id(image_id: int,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(
                                   auth_service.get_current_user)
                               ):
    pass


@router.get('/test_role/', response_model=CommentsResponce,
               dependencies=[Depends(RolesAccess([Role.admin, Role.moderator]))])
async def remove_images_comments_for_id(db: Session = Depends(get_db),
                                        current_user: User = Depends(
                                            auth_service.get_current_user)
                                        ):
    return CommentsResponce(comment = 'Hello', username = current_user.username, edit_date = str(current_user.created_at))
