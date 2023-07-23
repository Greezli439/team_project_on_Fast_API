from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.database.models import User, Role
from src.schemas import UserModel, UserResponse, TokenModel, ImageBase, ImageResponse
from src.repository import users as repository_users
from src.services.users import auth_service
from src.services.roles import RolesAccess

router = APIRouter(prefix='/images', tags=["images"])

security = HTTPBearer()

access_get = RolesAccess([Role.admin, Role.moderator, Role.user])
access_create = RolesAccess([Role.admin, Role.moderator, Role.user])
access_update = RolesAccess([Role.admin, Role.moderator])
access_delete = RolesAccess([Role.admin, Role.moderator])


@router.get('/', response_model=ImageBase, dependencies=[Depends(access_get)])
async def get_images(db: Session = Depends(get_db)):
    pass


@router.post('/', response_model=ImageBase, dependencies=[Depends(access_create)])
async def create_new_images(file: UploadFile = File(),
                            title: str = None,
                            tags: str = None,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(
                                auth_service.get_current_user)
                            ):
    pass


@router.get('/qrcode/{image_id}'""", response_model=ImageResponse знайти модель для поверненя зображення""",
            dependencies=[Depends(access_get)])
async def get_qr_for_id(image_id: int,
                            db: Session = Depends(get_db)):
    pass


@router.get('/{image_id}', response_model=ImageResponse,
            dependencies=[Depends(access_get)])
async def get_images_for_id(image_id: int,
                            db: Session = Depends(get_db)):
    pass

@router.delete('/{image_id}', response_model=ImageResponse, 
               dependencies=[Depends(access_delete)])
async def remove_images_for_id(image_id: int,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(
                                auth_service.get_current_user)
                               ):
    pass

@router.put('/{image_id}', response_model=ImageResponse)
async def set_new_title_images_for_id(image_id: int,
                                      title: str = None,
                                      tags: str = None,
                                      db: Session = Depends(get_db),
                                      current_user: User = Depends(
                                          auth_service.get_current_user)
                                      ):
    pass