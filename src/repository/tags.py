from typing import List, Type

from sqlalchemy.orm import Session

from src.database.models import Tag
from src.schemas import TagModel

async def get_tags(db: Session):
    """
    Retrieve a list of all tags from the database.

    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[Tag]: A list of Tag objects representing all the tags in the database.

    """
    return db.query(Tag).all()


async def get_tag(tag_id: int, db: Session) -> Type[Tag] | None:
    """
    Retrieve a tag from the database based on the provided tag ID.

    :param tag_id (int): The ID of the tag to retrieve.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Optional[Type[Tag]]: The Tag object representing the tag with the given ID if found,
                             or None if no tag with the provided ID exists in the database.

    """
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def create_tag(body: TagModel, db: Session) -> Tag:
    """
    Create a new tag and add it to the database.

    :param body (TagModel): The model containing the name of the new tag.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Tag: The newly created Tag object representing the new tag.
    """
    tag = Tag(name_tag=body.name_tag.lower())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def update_tag(tag_id: int, body: TagModel, db: Session) -> Tag | None:
    """
    Update the name of an existing tag in the database.

    :param tag_id (int): The ID of the tag to update.
    :param body (TagModel): The model containing the new name for the tag.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Optional[Tag]: The updated Tag object representing the tag with the new name if the update is successful,
                       or None if the tag with the provided ID does not exist or if the new tag name already exists in the database.

    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        new_tag_name_in_base = db.query(Tag).filter(Tag.name_tag == body.name_tag.lower()).first()
        if new_tag_name_in_base:
            return None
        tag.name_tag = body.name_tag.lower()
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session) -> Tag | None:
    """
    Remove a tag from the database based on the provided tag ID.

    :param tag_id (int): The ID of the tag to remove.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Optional[Tag]: The removed Tag object representing the tag with the provided ID if found and removed,
                       or None if no tag with the provided ID exists in the database.

    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag

 
async def remove_name_tag(name_tag: str, db: Session) -> Tag | None:
    """
    Remove a tag from the database based on the provided tag name.

    :param name_tag (str): The name of the tag to remove.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Optional[Tag]: The removed Tag object representing the tag with the provided name if found and removed,
                       or None if no tag with the provided name exists in the database.

    """
    tag = db.query(Tag).filter(Tag.name_tag == name_tag).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag


async def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    """
    Retrieve a tag from the database based on the provided tag name.

    :param tag_name (str): The name of the tag to retrieve.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Optional[Tag]: The Tag object representing the tag with the provided name if found,
                       or None if no tag with the provided name exists in the database.

    """
    tag = db.query(Tag).filter(Tag.name_tag == tag_name.lower()).first()
    return tag
