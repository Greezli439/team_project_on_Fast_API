from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Image, User, Tag, Comment, Role
from src.repository import tags
from src.routes import images
from src.schemas import ImageChangeSizeModel, ImageChangeColorModel, ImageTransformModel, ImageSignModel
from src.services.images import image_cloudinary


async def get_images(db: Session):
    images = db.query(Image).order_by(Image.id).all()

    user_response = []
    for image in images:
        comments = db.query(Comment).filter(Comment.image_id == image.id).all()
        user_response.append({"image": image, "comments": comments})

    return user_response


async def get_image(db: Session, id: int):
    image = db.query(Image).filter(Image.id == id).first()
    if image:
        comments = db.query(Comment).filter(Comment.image_id == image.id).all()
        return image, comments
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


async def add_image(db: Session, tags: list[str], url: str, title: str, description: str, user: User):
    if not user:
        return None

    detail = "Image was successfully created"
    num_tags = 0
    image_tags = []
    for tag in tags:
        if len(tag) > 25:
            tag = tag[0:25]
        if not db.query(Tag).filter(Tag.name == tag.lower()).first():
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
    db_image = Image(description=description, tags=tags, url=url, title=title, user_id=user.id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image, detail


async def delete_image(db: Session, id: int):
    db_image = db.query(Image).filter(Image.id == id).first()
    db.delete(db_image)
    db.commit()
    return db_image


async def change_size_image(body: ImageChangeSizeModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.change_size(body.title, body.height, body.width)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)


async def change_color_object_in_image(body: ImageChangeColorModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.change_color_object_in_image(image_name=body.title, object=body.object, color=body.color)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)


async def cut_face_in_image(body: ImageTransformModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.cut_face_in_image(image_name=body.title)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)


async def sign_image(body: ImageSignModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.sign_image(image_name=body.title, text=body.text)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)


async def expand_image(body: ImageTransformModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.expand_image(image_name=body.title)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)


async def vertically_expand_image(body: ImageTransformModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.vertically_expand_image(image_name=body.title)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)


async def fade_adges_image(body: ImageTransformModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.fade_adges_image(image_name=body.title)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)


async def make_black_white_image (body: ImageTransformModel, db: Session, user: User):
    url, new_imade_name =await image_cloudinary.make_black_white_image (image_name=body.title)
    return await add_image(db=db, tags=body.tags, url=url, title=new_imade_name, description=body.description,user=user)
