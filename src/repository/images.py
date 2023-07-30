import qrcode
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

import base64
import io
from PIL import Image

from src.database.models import Image, User, Tag, Comment, Role
from src.repository import tags
from src.routes import images

from src.schemas import ImageChangeSizeModel, ImageChangeColorModel, ImageTransformModel, ImageSignModel, ImageUpdateModel
from src.services.images import image_cloudinary


async def get_users_images(db: Session, user: User):
    response = []
    user_images = user.images
    user_img_id_list = [img.id for img in user_images]
    images = db.query(Image).order_by(Image.id).all()
    for image in images:
        if image.id in user_img_id_list:
            # db_tags = image.tags
            # tags_list = [tag.name_tag for tag in db_tags]
            # recent_comments = db.query(Comment).filter_by(image_id=image.id).order_by(desc(Comment.created_at)).limit(3).all()
            # comments_list = [comment.comment for comment in recent_comments]
            result = {'url': image.url, 'description': image.description}
            response.append(result)
    print(response)
    return {"images_response": response}


async def get_all_images(db: Session):
    response = []
    images = db.query(Image).order_by(Image.id).all()
    for image in images:
        db_tags = image.tags
        tags_list = [tag.name_tag for tag in db_tags]
        recent_comments = db.query(Comment).filter_by(image_id=image.id).order_by(desc(Comment.created_at)).limit(3).all()
        comments_list = [comment.comment for comment in recent_comments]
        result = {'url': image.url, 'description': image.description, 'tags_list': tags_list, 'comments_list': comments_list}
        response.append(result)
    return {"images_response": response}


async def get_image(db: Session, id: int, user: User):
    image = db.query(Image).filter(Image.id == id).first()
    if image:
        return image
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    

async def get_images_by_tag(tag_id: int, db: Session, user: User):
    response = []
    user_images = user.images
    user_img_list = [img for img in user_images]
    images = db.query(Image).filter(Image.id == tag_id).all()
    for image in images:
        if image in user_img_list:
            db_tags = image.tags
            tags_list = [tag.name_tag for tag in db_tags]
            recent_comments = db.query(Comment).filter_by(image_id=image.id).order_by(desc(Comment.created_at)).limit(3).all()
            comments_list = [comment.comment for comment in recent_comments]
            result = {'url': image.url, 'description': image.description, 'tags_list': tags_list, 'comments_list': comments_list}
            response.append(result)
    return {"images_response": response}
    

async def img_update_name(body:ImageUpdateModel, db: Session, user: User):
    pass


async def add_image(db: Session, tags: list[str], url: str, image_name: str, public_id: str, description: str, user: User):
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
    db_image = db.query(Image).filter(Image.id == id).first()
    await image_cloudinary.delete_image(db_image.public_id)
    db.delete(db_image)
    db.commit()
    return db_image


async def change_size_image(body: ImageChangeSizeModel, db: Session, user: User):

    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.change_size(db_image.public_id, body.width)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def change_color_object_in_image(body: ImageChangeColorModel, db: Session, user: User):

    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.change_color_object_in_image(public_id=db_image.public_id, object=body.object, color=body.color)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def cut_face_in_image(body: ImageTransformModel, db: Session, user: User):

    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.cut_face_in_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)

async def sign_image(body: ImageSignModel, db: Session, user: User):
    
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.sign_image(public_id=db_image.public_id, text=body.text)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def expand_image(body: ImageTransformModel, db: Session, user: User):
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.expand_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def vertically_expand_image(body: ImageTransformModel, db: Session, user: User):
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.vertically_expand_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def fade_adges_image(body: ImageTransformModel, db: Session, user: User):
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.fade_adges_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def make_black_white_image (body: ImageTransformModel, db: Session, user: User):
    db_image = db.query(Image).filter(Image.id == body.id).first()
    url, public_id =await image_cloudinary.make_black_white_image(public_id=db_image.public_id)
    new_image_name = image_cloudinary.create_new_name()
    db_tags = db_image.tags
    tags = [tag.name_tag for tag in db_tags]
    return await add_image(db=db, tags=tags, url=url, image_name=new_image_name, public_id=public_id, description=db_image.description,user=user)


async def get_qr_code(id: int, db: Session):
    db_image = db.query(Image).filter(Image.id == id).first()
    qr = qrcode.QRCode()
    qr.add_data(db_image.url)
    qr.make(fit=True)
    qr_code_img = qr.make_image(fill_color="black", back_color="white")
    img_byte_array = io.BytesIO()
    qr_code_img.save(img_byte_array, format='PNG')

    base64_encoded_img = base64.b64encode(img_byte_array.getvalue()).decode('utf-8')

    return base64_encoded_img