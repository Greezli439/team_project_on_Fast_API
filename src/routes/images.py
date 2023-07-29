import uuid

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.services.users import auth_service

from src.database.db_connection import get_db
from src.database.models import User
from src.schemas import ImageGetAllResponse, ImageNameUpdateModel, ImageNameUpdateResponse, \
    ImageGetResponse, ImageAddTagResponse, ImageModel, ImageUpdateModel, ImageSignModel, ImageAddResponse, ImageDeleteResponse, \
    ImageAddModel, ImageChangeSizeModel, ImageChangeColorModel, ImageTransformModel
from src.repository import users as repository_users
from src.repository import images as repository_images
from src.services.roles import access_AM, access_AU, access_A
from src.services.images import image_cloudinary
from src.services.users import auth_service


router = APIRouter(prefix='/images', tags=["images"])

security = HTTPBearer()


@router.get("/{image_id}", response_model=ImageGetResponse)
async def get_image(image_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    response = await repository_images.get_image(db, image_id, current_user)
    return response


@router.get("/{user_id}", response_model=List[ImageGetResponse])
async def get_current_user_images(user_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    images_response = await repository_images.get_current_user_images(db, user_id, current_user)
    return images_response


@router.get("/", response_model=List[ImageGetResponse])
async def get_all_images(db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    images = await repository_images.get_all_images(db)
    return images


@router.get("/{tag_id}", response_model=ImageGetAllResponse)
async def get_image_by_tag(tag_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    response = await repository_images.get_images_by_tag(tag_id, db, current_user)
    return response


@router.put('/{image_id}', response_model=ImageModel)
async def update_image(body: ImageUpdateModel, image_id:int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    image = await repository_images.img_update(body, image_id, db, current_user)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return image


@router.post('/', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def create_new_images(file: UploadFile = File(),
                            image_name: str = None,
                            description: str = None,
                            tags: str = None,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents =  await file.read()
    url, public_id = await image_cloudinary.add_image(contents)
    tags_list = tags.replace(",", " ").replace(".", " ").replace("/", " ").split()
    db_image, detail = await repository_images.add_image(db=db, 
                                                         url=url, 
                                                         tags=tags_list, 
                                                         image_name=image_name, 
                                                         public_id=public_id, 
                                                         description=description, 
                                                         user=current_user)
    return {"image": db_image, "details": detail}


@router.delete("/{id}", response_model=ImageDeleteResponse, dependencies=[Depends(access_AU)])
async def delete_image(id: int, db: Session = Depends(get_db), 
                       current_user: User = Depends(auth_service.get_current_user)):
    db_image = await repository_images.delete_image(db, id, current_user)
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
async def change_color_image(body: ImageChangeColorModel, 
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
    db_image, detail = await repository_images.sign_image(body=body, db=db, user = current_user)
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


@router.get('/qrcode/')
async def get_qr_code(id: int, db: Session = Depends(get_db)):
    print('$'*80)
    qr_image = await repository_images.get_qr_code(id, db)
    return qr_image
