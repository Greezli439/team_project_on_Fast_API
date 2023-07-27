import uuid

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.services.users import auth_service

from src.database.db_connection import get_db
from src.database.models import User
from src.schemas import ImageGetAllResponse, ImageUpdateDescrResponse, \
    ImageGetResponse, ImageAddTagResponse, ImageSignModel, ImageAddResponse, ImageDeleteResponse, ImageAddModel, ImageChangeSizeModel, ImageChangeColorModel, ImageTransformModel
from src.repository import users as repository_users
from src.repository import images as repository_images
from src.services.roles import access_AM, access_AU, access_A
from src.services.images import image_cloudinary
from src.services.users import auth_service

# from src.services.auth import auth_service

router = APIRouter(prefix='/images', tags=["images"])

security = HTTPBearer()


@router.get('/qrcode/{image_id}'""", response_model=ImageResponse знайти модель для поверненя зображення""")
async def get_qr_for_id(image_id: int,
                        db: Session = Depends(get_db)):
    pass


@router.get("", response_model=ImageGetAllResponse)
async def get_images(db: Session = Depends(get_db)):
    user_images = await repository_images.get_images(db)
    return {"images": user_images}


@router.get("/image_id/{id}", response_model=ImageGetResponse)
async def get_image(id: int, db: Session = Depends(get_db)):
    user_image, comments = await repository_images.get_image(db, id)
    return {"image": user_image, "comments": comments}


##########Тут має бути завантаження на Cloudinary
@router.post('/', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def create_new_images(file: UploadFile = File(),
                            title: str = None,
                            description: str = None,
                            tags: str = None,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents =  await file.read()
    url = await image_cloudinary.add_image(contents, title)
    tags_list = [tag for tag in tags.split(',')]
    db_image, detail = await repository_images.add_image(db=db, url=url, tags=tags_list, title=title, description=description, user=current_user)
    return {"image": db_image, "details": detail}


@router.delete("/{id}", response_model=ImageDeleteResponse, dependencies=[Depends(access_AU)])
async def delete_image(id: int, db: Session = Depends(get_db)):
    db_image = await repository_images.delete_image(db, id)
    return {"image": db_image, "details": "Image was successfully deleted"}


@router.post('/change_size', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def change_size_image(body: ImageChangeSizeModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.change_size_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/change_color', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def change_size_image(body: ImageChangeColorModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.change_color_object_in_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/cut_face', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def cut_face_in_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.cut_face_in_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/sign_image', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def sign_image(body: ImageSignModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.cut_face_in_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}

@router.post('/expand', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def expand_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.expand_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}

@router.post('/vertically_expand', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def vertically_expand_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.vertically_expand_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}

@router.post('/fade_adges', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def fade_adges_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.fade_adges_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}

@router.post('/black_white', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def make_black_white_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    db_image, detail = await repository_images.make_black_white_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}

