import qrcode
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_


import base64
import io
from PIL import Image

from src.database.models import Image, User, Tag, Comment, Role
from src.repository import tags as t
from src.routes import images

from src.schemas import ImageChangeSizeModel, ImageChangeColorModel, ImageTransformModel, ImageSignModel, ImageUpdateModel
from src.services.images import image_cloudinary


async def get_current_user_images(db: Session, user_id: int):
    """
    Retrieve images belonging to the specified user.

    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user_id (int): The ID of the user whose images to retrieve.

    :return: List[Image] or None: A list of Image objects representing the images associated with the user.
    """
    images = db.query(Image).filter(Image.user_id == user_id).all()
    if images:
        return images
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


async def get_all_images(db: Session):
    """
    Retrieve all images from the database.

    :param db (Session): The SQLAlchemy database session to use for the query.

    :return: List[Image] or None: A list of Image objects representing all the images in the database.
    """
    images = db.query(Image).join(Image.username).order_by(Image.id).all()
    if images:
        return images
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


async def get_image(db: Session, id: int, user: User):
    """
    Retrieve an image by  image ID, ensuring it belongs to the specified user.

    :param db (Session): The SQLAlchemy database session to use for the query.
    :param id (int): The ID of the image to retrieve.
    :param user (User): The user object representing the user requesting the image.

    :return: Optional[Image]: The Image object representing the requested image if it belongs to the specified user.

    """
    image = db.query(Image).filter(Image.id == id).first()
    if image:
        return image
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    


async def get_images_by_tag(id: int, db: Session):
    """
    Retrieve images associated with a specific tag.

    :param id (int): The ID of the tag to search for.
    :param db (Session): The SQLAlchemy database session to use for the query.

    :return: List[Image]: A list of Image objects representing the images associated with the specified tag.

    """
    images = db.query(Image).join(Image.tags).join(Image.username).filter(Tag.id == id).all()
    if images:
        return [image for image in images]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    

async def img_update(body:ImageUpdateModel, image_id: int, db: Session, user: User):
    """
    Update an existing image with the provided information.

    :param body (ImageUpdateModel): The model containing the updated image information.
    :param image_id (int): The ID of the image to update.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user making the update.
    :return: Image: The updated Image object.

    """
    image = db.query(Image).filter(
        and_(Image.id == image_id, Image.user_id == user.id)).first()
    if image:
        for old_tag in image.tags:
            t.remove_tag(old_tag.id,db)
        tags_list = body.tags.replace(",", "").replace(".", "").replace("/", "").split()
        num_tags = 0
        image_tags = []
        for tag in tags_list:
            if len(tag) > 25:
                tag = tag[0:25]
            if not db.query(Tag).filter(Tag.name_tag == tag.lower()).first():
                db_tag = Tag(name_tag=tag.lower())
                db.add(db_tag)
                db.commit()
                db.refresh(db_tag)
            if num_tags < 5:
                image_tags.append(tag.lower())
            num_tags += 1

        if num_tags >= 5:
            detail = "Maximum 5 tags per image allowed!"

        tags = db.query(Tag).filter(Tag.name_tag.in_(image_tags)).all()
        image.image_name = body.image_name
        image.description = body.description
        image.tags = tags # доробити
        db.commit()
    return image


async def add_image(db: Session, tags: list[str], url: str, image_name: str, public_id: str, description: str, user: User):
    """
    Add a new image to the database.

    :param db (Session): The SQLAlchemy database session to use for the query.
    :param tags (List[str]): A list of strings representing the tags associated with the image.
    :param url (str): The URL of the image.
    :param image_name (str): The name of the image.
    :param public_id (str): The public ID of the image.
    :param description (str): The description of the image.
    :param user (User): The user object representing the user who uploaded the image.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the added image.
            str: A message indicating the status of the image creation process.
    """
    if not user:
        return None

    detail = "Image was successfully created"
    num_tags = 0
    image_tags = []
    for tag in tags:
        if len(tag) > 25:
            tag = tag[0:25]
        if not db.query(Tag).filter(Tag.name_tag == tag.lower()).first():
            db_tag = Tag(name_tag=tag.lower())
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        if num_tags < 5:
            image_tags.append(tag.lower())
        num_tags += 1

    if num_tags >= 5:
        detail = "Maximum 5 tags per image allowed!"

    tags = db.query(Tag).filter(Tag.name_tag.in_(image_tags)).all()
    db_image = Image(description=description, tags=tags, url=url, image_name=image_name, public_id=public_id, user_id=user.id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image, detail


async def delete_image(db: Session, id: int, user: User):
    """
    Delete an image from the database and the corresponding image from the cloud storage.

    :param db (Session): The SQLAlchemy database session to use for the query.
    :param id (int): The ID of the image to delete.
    :param user (User): The user object representing the user who owns the image.

    :return:Image: The Image object that was deleted.
    """
    db_image = db.query(Image).filter(Image.id == id).first()
    await image_cloudinary.delete_image(db_image.public_id)
    db.delete(db_image)
    db.commit()
    return db_image


async def change_size_image(body: ImageChangeSizeModel, db: Session, user: User):
    """
    Change the size of an existing image and add the updated image to the database.

    :param body (ImageChangeSizeModel): The model containing the image ID and the new width.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is changing the image size.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the updated image.
            str: A message indicating the status of the image size change process.

    """
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.change_size(db_image.public_id, body.width)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def change_color_object_in_image(body: ImageChangeColorModel, db: Session, user: User):
    """
    Change the color of a specific object in an existing image and add the updated image to the database.

    :param body (ImageChangeColorModel): The model containing the image ID, object to change color, and the new color.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is changing the color.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the updated image.
            str: A message indicating the status of the object color change process.

    """
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.change_color_object_in_image(public_id=db_image.public_id, object=body.object, color=body.color)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def cut_face_in_image(body: ImageTransformModel, db: Session, user: User):
    """    
    Perform a face-cut transformation on an existing image and add the transformed image to the database.

    :param body (ImageTransformModel): The model containing the image ID and other transformation-related attributes if applicable.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is performing the image transformation.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the transformed image.
            str: A message indicating the status of the image transformation process.
"""
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.cut_face_in_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def sign_image(body: ImageSignModel, db: Session, user: User):
    """
    Sign an existing image with the provided text and add the signed image to the database.

    :param body (ImageSignModel): The model containing the image ID and the text for signing.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is signing the image.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the signed image.
            str: A message indicating the status of the image signing process.

    """
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.sign_image(public_id=db_image.public_id, text=body.text)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def expand_image(body: ImageTransformModel, db: Session, user: User):
    """
    Expand an existing image and add the expanded image to the database.

    :param body (ImageTransformModel): The model containing the image ID and other transformation-related attributes if applicable.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is performing the image expansion.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the expanded image.
            str: A message indicating the status of the image expansion process.
"""
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.expand_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def vertically_expand_image(body: ImageTransformModel, db: Session, user: User):
    """
    Vertically expand an existing image and add the vertically expanded image to the database.

    :param body (ImageTransformModel): The model containing the image ID and other transformation-related attributes if applicable.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is performing the image vertical expansion.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the vertically expanded image.
            str: A message indicating the status of the image vertical expansion process.
"""
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.vertically_expand_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def fade_adges_image(body: ImageTransformModel, db: Session, user: User):
    """
    Synchronously fade the edges of an existing image and add the faded image to the database.

    :param body (ImageTransformModel): The model containing the image ID and other transformation-related attributes if applicable.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is fading the edges of the image.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the faded image.
            str: A message indicating the status of the image fading process.
    """
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.fade_adges_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def make_black_white_image (body: ImageTransformModel, db: Session, user: User):
    """
    Convert an existing image to black and white and add the converted image to the database.

    :param body (ImageTransformModel): The model containing the image ID and other transformation-related attributes if applicable.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param user (User): The user object representing the user who is converting the image to black and white.

    Returns:
        tuple: A tuple containing:
            Image: The newly created Image object representing the black and white converted image.
            str: A message indicating the status of the black and white conversion process.
    """
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.make_black_white_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def get_qr_code(id: int, db: Session):
    """
    Generate a QR code image from the URL of an existing image.

    :param id (int): The ID of the image to generate the QR code for.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        bytes or None: A bytes object representing the QR code image in PNG format,
                       or None if the image with the specified ID does not exist.

    """
    db_image = db.query(Image).filter(Image.id == id).first()
    qr = qrcode.QRCode()
    qr.add_data(db_image.url)
    qr.make(fit=True)
    qr_code_img = qr.make_image(fill_color="black", back_color="white")
    img_byte_array = io.BytesIO()
    qr_code_img.save(img_byte_array, format='PNG')

    base64_encoded_img = base64.b64encode(img_byte_array.getvalue()).decode('utf-8')
    return base64_encoded_img
