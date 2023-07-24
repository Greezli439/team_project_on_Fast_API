from typing import List, Type

from sqlalchemy.orm import Session

from src.database.models import Tag
from src.schemas import TagModel


async def get_tags(db: Session):
    return db.query(Tag).all()


async def get_tag(tag_id: int, db: Session) -> Type[Tag] | None:
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def create_tag(body: TagModel, db: Session) -> Tag:
    tag = Tag(name_tag=body.name_tag.lower())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def update_tag(tag_id: int, body: TagModel, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        new_tag_name_in_base = db.query(Tag).filter(Tag.name_tag == body.name_tag.lower()).first()
        if new_tag_name_in_base:
            return None
        tag.name_tag = body.name_tag.lower()
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session) -> Tag | None:

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session) -> Tag | None:

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag


async def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.name_tag == tag_name.lower()).first()
    return tag
