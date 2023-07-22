from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.schemas import UserModel, UserResponse, TokenModel, ImageBase, ImageResponse
from src.repository import users as repository_users
# from src.services.auth import auth_service

router = APIRouter(prefix='/images', tags=["images"])

security = HTTPBearer()


@router.get('/', response_model=ImageBase)
async def get_images(db: Session = Depends(get_db)):
    pass

@router.post('/', response_model=ImageBase)
async def create_new_images(file: UploadFile = File(),
                            title: str = None,
                            tags: str = None,
                            db: Session = Depends(get_db),
                            ):
    pass


@router.get('/qrcode/{image_id}'""", response_model=ImageResponse знайти модель для поверненя зображення""")
async def get_qr_for_id(image_id: int,
                            db: Session = Depends(get_db)):
    pass


@router.get('/{image_id}', response_model=ImageResponse)
async def get_images_for_id(image_id: int,
                            db: Session = Depends(get_db)):
    pass

@router.delete('/{image_id}', response_model=ImageResponse)
async def remove_images_for_id(image_id: int,
                               db: Session = Depends(get_db)):
    pass

@router.put('/{image_id}', response_model=ImageResponse)
async def set_new_title_images_for_id(image_id: int,
                                      title: str = None,
                                      tags: str = None,
                                      db: Session = Depends(get_db)):
    pass