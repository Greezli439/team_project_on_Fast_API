from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.services.users import auth_service

from src.database.db_connection import get_db
from src.database.models import Image, User
from src.services.roles import access_AM, access_AU, access_A
from src.services.users import Auth
from src.repository import users as repository_users

from src.schemas import UserModel, UserResponse, TokenModel, CommentResponse, CommentModel, CommentDeleteResponse, CommentModelUpdate
from src.repository import comments as repository_comments


router = APIRouter(prefix='/comments', tags=["comments"])

security = HTTPBearer()


@router.get('/', response_model=List[CommentResponse], dependencies=[Depends(access_A)])
async def get_comments(db: Session = Depends(get_db)):
    """
        Get all comments from the database.

    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[CommentResponse]: A list of CommentResponse objects representing all the comments.

    """
    comments = await repository_comments.get_comments(db)
    return comments

@router.post('/', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
        Create a new comment for an image with the provided ID.

    :param body (CommentModel): The data for creating the comment as a CommentModel object.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        CommentResponse: A CommentResponse object representing the created comment.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such image"):
            If the image with the provided ID is not found.

    """
    image = db.query(Image).filter_by(id=body.image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such image")
    comment = await repository_comments.create_comment(body, current_user, db)
    return comment


@router.get('/{comment_id}', response_model=CommentResponse)
async def get_comment_by_id(comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                            _: User = Depends(auth_service.get_current_user)):
    """
       Get a comment by its unique ID.

    :param comment_id (int): The ID of the comment to retrieve. Must be greater than or equal to 1.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param _: User: The User object representing the authenticated user. This parameter is ignored and not used in the function.

    Returns:
        CommentResponse: A CommentResponse object representing the retrieved comment.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment"):
            If the comment with the provided ID is not found.

    """
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment


@router.get('/image/{image_id}', response_model=List[CommentResponse])
async def get_comment_by_image_id(image_id: int = Path(ge=1), db: Session = Depends(get_db),
                                  _: User = Depends(auth_service.get_current_user)):
    """
        Get comments for an image with the provided image ID.

    :param image_id (int): The ID of the image for which to retrieve comments. Must be greater than or equal to 1.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param _: User: The User object representing the authenticated user. This parameter is ignored and not used in the function.

    Returns:
        List[CommentResponse]: A list of CommentResponse objects representing the comments for the image.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such photo"):
            If the image with the provided ID is not found.

    """
    comment = await repository_comments.get_comments_for_photo(image_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such photo")
    return comment


@router.put('/{comment_id}', response_model=CommentResponse)
async def update_comment(body: CommentModelUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
        Update a comment with the provided changes.

    :param body (CommentModelUpdate): The CommentModelUpdate object containing the updated comment data.
    :param db (Session): The SQLAlchemy database session to use for the update operation.
    :param current_user (User): The User object representing the authenticated user.

    Returns:
        CommentResponse: A CommentResponse object representing the updated comment.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment"):
            If the comment with the provided ID is not found.
        HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't change not your comment"):
            If the authenticated user is not the author of the comment and is not a moderator or admin.

    """
    comment = await repository_comments.update_comment(body, db, current_user)
    return comment


@router.delete('/{comment_id}', response_model=CommentDeleteResponse, dependencies=[Depends(access_AM)])
async def remove_comment(comment_id: int = Path(ge=1), db: Session = Depends(get_db)):
    """
        Remove a comment with the provided comment ID.

    :param comment_id (int): The ID of the comment to be removed. Must be greater than or equal to 1.
    :param db (Session): The SQLAlchemy database session to use for the delete operation.

    Returns:
        CommentDeleteResponse: A CommentDeleteResponse object representing the deleted comment.

    Raises:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment"):
            If the comment with the provided ID is not found.

    """
    comment = await repository_comments.remove_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment
