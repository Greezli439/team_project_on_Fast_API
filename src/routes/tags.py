from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.services.users import auth_service

from src.database.db_connection import get_db
from src.schemas import UserModel, UserResponse, TokenModel, TagResponse, TagModel
from src.repository import tags as repository_tags
from src.services.roles import access_AM, access_AU, access_A

# from src.services.auth import auth_service

router = APIRouter(prefix='/tags', tags=["tags"])

security = HTTPBearer()


@router.get("/", response_model=List[TagResponse])
async def get_all_tag(db: Session = Depends(get_db)):
    """
        Get all tags from the database.

    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[TagResponse]: A list of TagResponse objects representing all the tags in the database.

    """
    tags = await repository_tags.get_tags(db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """
        Retrieve a specific tag by its ID.

    :param tag_id (int): The ID of the tag to retrieve.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        TagResponse: A TagResponse object representing the retrieved tag.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"):
            If the tag with the provided ID is not found.

    """
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse)
async def create_tag(body: TagModel, db: Session = Depends(get_db)):
    """
        Create a new tag.

    :param body (TagModel): The TagModel object containing the name of the new tag to create.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        TagResponse: A TagResponse object representing the created tag.

    Raises:
        HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Such tag already exist'):
            If a tag with the same name already exists.
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST):
            If the tag creation request is malformed.

    """
    check_tag = await repository_tags.get_tag_by_name(body.name_tag.lower(), db)
    if check_tag:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Such tag already exist')
    tag = await repository_tags.create_tag(body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return tag


@router.put("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_AM)])
async def update_tag(body: TagModel, tag_id: int, db: Session = Depends(get_db)):
    """
        Update an existing tag.

    :param body (TagModel): The TagModel object containing the updated tag name.
    :param tag_id (int): The ID of the tag to update.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        TagResponse: A TagResponse object representing the updated tag.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail="Tag not found or you don't have enough rules to update"):
            If the tag with the specified ID does not exist, or the user does not have sufficient
            privileges to update the tag.

    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to update")
    return tag


@router.delete("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_AM)])
async def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    """
        Remove a tag by its ID.

    :param tag_id (int): The ID of the tag to remove.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        TagResponse: A TagResponse object representing the removed tag.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail="Tag not found or you don't have enough rules to delete"):
            If the tag with the specified ID does not exist, or the user does not have sufficient
            privileges to delete the tag.

    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to delete")
    return tag
    

@router.delete("/nametag/{name_tag}", response_model=TagResponse, dependencies=[Depends(access_AM)])
async def remove_name_tag(name_tag: str, db: Session = Depends(get_db)):
    """
        Remove a tag by its name.

    :param name_tag (str): The name of the tag to remove.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        TagResponse: A TagResponse object representing the removed tag.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail="Tag not found or you don't have enough rules to delete"):
            If the tag with the specified name does not exist, or the user does not have sufficient
            privileges to delete the tag.

    """
    tag = await repository_tags.remove_name_tag(name_tag, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to delete")
    return tag

