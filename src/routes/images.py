import uuid

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.services.users import auth_service

from src.database.db_connection import get_db
from src.database.models import User
from src.schemas import ImageGetAllResponse, ImageNameUpdateModel, ImageNameUpdateResponse, \
    ImageGetResponse, ImageAddTagResponse, ImageSignModel, ImageAddResponse, ImageDeleteResponse, \
    ImageAddModel, ImageChangeSizeModel, ImageChangeColorModel, ImageTransformModel, GetQRCode, \
    ImageModel, ImageUpdateModel

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
    """
        Retrieve an image based on the provided image ID and authenticated user.

    :param image_id (int): The ID of the image to retrieve.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (Optional[User]): The User object representing the authenticated user, if available.

    Returns:
        ImageGetResponse: The ImageGetResponse object representing the retrieved image.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    response = await repository_images.get_image(db, image_id, current_user)
    return response


@router.get("/user/{user_id}", response_model=List[ImageGetResponse])
async def get_current_user_images(user_id: int, db: Session = Depends(get_db)):
    """
        Retrieve a list of images for the specified user based on the provided user ID.

    :param user_id (int): The ID of the user for whom to retrieve the images.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[ImageGetResponse]: A list of ImageGetResponse objects representing the images associated with the user.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    images_response = await repository_images.get_current_user_images(db, user_id)
    return images_response


@router.get("/", response_model=List[ImageGetResponse])
async def get_all_images(db: Session = Depends(get_db)):
    """
        Retrieve a list of all images available in the database.

    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[ImageGetResponse]: A list of ImageGetResponse objects representing all the images available.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    images = await repository_images.get_all_images(db)
    return images



@router.get("/tag/{tag_id}", response_model=List[ImageGetResponse])
async def get_image_by_tag(tag_id: int, db: Session = Depends(get_db)):
    """
        Retrieve a list of images associated with the specified tag based on the provided tag ID.

    :param tag_id (int): The ID of the tag for which to retrieve the images.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[ImageGetResponse]: A list of ImageGetResponse objects representing the images associated with the tag.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    response = await repository_images.get_images_by_tag(tag_id, db)

    return response


@router.put('/{image_id}', response_model=ImageModel)
async def update_image(body: ImageUpdateModel, image_id:int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
        Update an image based on the provided image ID, updated image data, and authenticated user.

    :param body (ImageUpdateModel): The updated image data as an ImageUpdateModel object.
    :param image_id (int): The ID of the image to update.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageModel: The ImageModel object representing the updated image.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
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
    """
        Create a new image based on the provided image data and authenticated user.

    :param file (UploadFile): The uploaded image file as an UploadFile object.
    :param image_name (str): The name of the image.
    :param description (str): The description of the image.
    :param tags (str): The tags of the image (comma-separated).
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the added image and additional details.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
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
    """
        Delete an image based on the provided image ID and authenticated user.

    :param id (int): The ID of the image to delete.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageDeleteResponse: An ImageDeleteResponse object containing the deleted image and additional details.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image = await repository_images.delete_image(db, id, current_user)
    return {"image": db_image, "details": "Image was successfully deleted"}


@router.post('/change_size', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def change_size_image(body: ImageChangeSizeModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """    
    Change the size of an image based on the provided image data and authenticated user.

    :param body (ImageChangeSizeModel): The data for changing the size of the image as an ImageChangeSizeModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the modified image and additional details.
    
    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image, detail = await repository_images.change_size_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/change_color', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def change_color_image(body: ImageChangeColorModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """
       Change the color of an object in an image based on the provided image data and authenticated user.

    :param body (ImageChangeColorModel): The data for changing the color of the image as an ImageChangeColorModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        Im:param ageAddResponse: An ImageAddResponse object containing the modified image and additional details.
    
    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image, detail = await repository_images.change_color_object_in_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/cut_face', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def cut_face_in_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """
        Cut the face from an image based on the provided image data and authenticated user.

    :param body (ImageTransformModel): The data for transforming the image as an ImageTransformModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the modified image and additional details.
    
    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image, detail = await repository_images.cut_face_in_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/sign_image', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def sign_image(body: ImageSignModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """
        Sign an image based on the provided image data and authenticated user.

    :param body (ImageSignModel): The data for signing the image as an ImageSignModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the modified image and additional details.
    
    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image, detail = await repository_images.sign_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/expand', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def expand_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """
        Expand an image based on the provided image data and authenticated user.

    :param body (ImageTransformModel): The data for expanding the image as an ImageTransformModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the modified image and additional details.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image, detail = await repository_images.expand_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/vertically_expand', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def vertically_expand_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """
        Vertically expand an image based on the provided image data and authenticated user.

    :param body (ImageTransformModel): The data for vertically expanding the image as an ImageTransformModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the modified image and additional details.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image, detail = await repository_images.vertically_expand_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/fade_adges', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def fade_adges_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """
        Fade the edges of an image based on the provided image data and authenticated user.

    :param body (ImageTransformModel): The data for fading the edges of the image as an ImageTransformModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the modified image and additional details.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.    
    """
    db_image, detail = await repository_images.fade_adges_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.post('/black_white', response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED)
async def make_black_white_image(body: ImageTransformModel, 
                            db: Session = Depends(get_db), 
                            current_user: User = Depends(auth_service.get_current_user)):
    """
        Convert an image to black and white based on the provided image data and authenticated user.

    :param body (ImageTransformModel): The data for converting the image to black and white as an ImageTransformModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        ImageAddResponse: An ImageAddResponse object containing the modified image and additional details.
    
    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.
    """
    db_image, detail = await repository_images.make_black_white_image(body=body, db=db, user = current_user)
    if db_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {"image": db_image, "details": detail}


@router.get('/qrcode/{id}', response_model=GetQRCode)
async def get_qr_code(id: int, db: Session = Depends(get_db)):
    """
        Generate a QR code for an image with the provided ID.

    :param id (int): The ID of the image for which to generate the QR code.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        GetQRCode: A GetQRCode object containing the ID of the image and the base64-encoded representation of the QR code image.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found"):
            If the image with the provided ID is not found.

    """
    base64_encoded_img = await repository_images.get_qr_code(id, db)
    if not base64_encoded_img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return {'id': id, 'base64_encoded_img': base64_encoded_img}

