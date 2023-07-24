from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.schemas import UserModel, UserResponse, TokenModel, ImageGetAllResponse, ImageUpdateDescrResponse, \
    ImageUpdateModel, ImageGetResponse, ImageAddTagResponse, ImageAddTagModel, ImageAddResponse, ImageDeleteResponse
from src.repository import users as repository_users, images

# from src.services.auth import auth_service

router = APIRouter(prefix='/images', tags=["images"])

security = HTTPBearer()


@router.get('/qrcode/{image_id}'""", response_model=ImageResponse знайти модель для поверненя зображення""")
async def get_qr_for_id(image_id: int,
                        db: Session = Depends(get_db)):
    pass


@router.get("", response_model=ImageGetAllResponse)
async def get_images(db: Session = Depends(get_db)):
    user_images = await images.get_images(db)
    return {"images": user_images}


@router.get("/image_id/{id}", response_model=ImageGetResponse)
async def get_image(id: int, db: Session = Depends(get_db)):
    user_image, comments = await images.get_image(db, id)
    return {"image": user_image, "comments": comments}


##########Тут має бути завантаження на Cloudinary
@router.post('/', response_model=ImageAddResponse)
async def create_new_images(file: UploadFile = File(),
                            title: str = None,
                            tags: str = None,
                            db: Session = Depends(get_db),
                            ):
    pass


@router.delete("/{id}", response_model=ImageDeleteResponse)
async def delete_image(id: int, db: Session = Depends(get_db)):
    user_image = await images.delete_image(db, id)
    return {"image": user_image, "detail": "Image was successfully deleted"}
