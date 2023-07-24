from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Image, User, Tag, Comment, Role
from src.repository import tags
from src.routes import images
from src.schemas import ImageUpdateModel, ImageAddModel, ImageAddTagModel


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


async def add_image(db: Session, image: ImageAddModel, tags: list[str], url: str, title: str, user: User):
    if not user:
        return None

    detail = ""
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
    db_image = Image(description=image.description, tags=tags, url=url, title=title, user_id=user.id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image, detail


async def delete_image(db: Session, id: int):
    db_image = db.query(Image).filter(Image.id == id).first()
    db.delete(db_image)
    db.commit()
    return db_image


